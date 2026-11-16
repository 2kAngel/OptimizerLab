"""
Adaptador genérico de problemas de ingeniería para pymoo.
Mapea cualquier EngineeringModule a un problema de optimización multi-objetivo con restricciones.
"""

import numpy as np
from typing import Any, Dict, List
from pymoo.core.problem import Problem
from backend.core.module_registry.base import EngineeringModule


class DesignLabOptimizationProblem(Problem):
    """
    Representa un problema de optimización multi-objetivo acoplado a un EngineeringModule de DesignLab.
    """

    def __init__(
        self,
        module: EngineeringModule,
        family_id: str,
        operating_conditions: Dict[str, Any],
    ):
        self.module = module
        self.family_id = family_id
        self.operating_conditions = operating_conditions

        # 1. Parámetros y límites según escala
        scale = str(self.operating_conditions.get("scale", "domestic")).lower()
        if hasattr(self.module, "get_parameters_for_scale"):
            self.param_defs = self.module.get_parameters_for_scale(family_id, scale)
        else:
            self.param_defs = self.module.get_parameters(family_id)

        # Filtrar solo parámetros numéricos para optimización continua
        self.continuous_params = [
            p for p in self.param_defs if p.data_type in {"float", "int"} and p.min_value is not None and p.max_value is not None
        ]
        self.n_var = len(self.continuous_params)
        self.param_names = [p.name for p in self.continuous_params]

        xl = np.array([float(p.min_value) for p in self.continuous_params])
        xu = np.array([float(p.max_value) for p in self.continuous_params])

        # 2. Objetivos
        self.obj_defs = self.module.get_objectives(family_id)
        self.n_obj = len(self.obj_defs)
        self.obj_names = [o.name for o in self.obj_defs]

        # 3. Restricciones según escala
        if hasattr(self.module, "get_constraints_for_scale"):
            self.constraint_defs = self.module.get_constraints_for_scale(family_id, scale)
        else:
            self.constraint_defs = self.module.get_constraints(family_id)
        n_ieq_constr = len(self.constraint_defs)

        super().__init__(
            n_var=self.n_var,
            n_obj=self.n_obj,
            n_ieq_constr=n_ieq_constr,
            xl=xl,
            xu=xu,
        )

        # Historial de evaluaciones registradas durante la evolución
        self.evaluated_candidates: List[Dict[str, Any]] = []

    def _evaluate(self, X: np.ndarray, out: Dict[str, Any], *args, **kwargs):
        pop_size = len(X)
        F = np.zeros((pop_size, self.n_obj))
        n_ieq = self.n_ieq_constr
        G = np.zeros((pop_size, n_ieq)) if n_ieq > 0 else None

        for i in range(pop_size):
            # Mapear vector continuo X[i] al diccionario de parámetros tipado
            param_dict = {}
            for idx, p_def in enumerate(self.continuous_params):
                val = float(X[i, idx])
                if p_def.data_type == "int":
                    val = int(round(val))
                param_dict[p_def.name] = val

            # Parámetros por defecto para los que no sean continuos
            for p_def in self.param_defs:
                if p_def.name not in param_dict and p_def.default_value is not None:
                    param_dict[p_def.name] = p_def.default_value

            # Evaluación rápida Nivel 1 del módulo
            eval_res = self.module.evaluate_fast(self.family_id, param_dict, self.operating_conditions)
            metrics = eval_res.metrics

            # Rellenar objetivos en F
            # En pymoo todos los objetivos se MINIMIZAN por defecto.
            # Si un objetivo en DesignLab es "maximize", se multiplica por -1.0
            for j, o_def in enumerate(self.obj_defs):
                val = metrics.get(o_def.name, 0.0)
                if o_def.direction == "maximize":
                    F[i, j] = -float(val)
                else:
                    F[i, j] = float(val)

            # Rellenar restricciones en G (pymoo requiere G <= 0 para que sea admisible)
            if G is not None:
                for k, c_def in enumerate(self.constraint_defs):
                    metric_val = metrics.get(c_def.name, 0.0)
                    limit = float(c_def.limit_value) if c_def.limit_value is not None else 0.0
                    if c_def.constraint_type == "lte":
                        # metric <= limit  -->  metric - limit <= 0
                        G[i, k] = float(metric_val - limit)
                    elif c_def.constraint_type == "gte":
                        # metric >= limit  -->  limit - metric <= 0
                        G[i, k] = float(limit - metric_val)
                    else:
                        G[i, k] = 0.0

            # Guardar en historial
            self.evaluated_candidates.append({
                "parameters": param_dict,
                "metrics": metrics,
                "is_valid": eval_res.is_valid,
            })

        out["F"] = F
        if G is not None:
            out["G"] = G
