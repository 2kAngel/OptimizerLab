"""
Sintetizador Generativo de Arquitecturas Eólicas asistido por Prompt para DesignLab.
Interpreta solicitudes en lenguaje natural y las traduce a topologías, parámetros físicos,
geometría procedural 3D y evaluación aerodinámica multiobjetivo.
"""

import re
import math
from typing import Any, Dict, Tuple


def parse_prompt_intent(prompt: str, default_scale: str = "domestic") -> Tuple[str, str, Dict[str, Any]]:
    """
    Analiza el prompt del usuario y determina:
    - family_id: La arquitectura aerodinámica más adecuada.
    - scale: Escala física (domestic, medium, large).
    - overrides: Parámetros numéricos específicos extraídos del texto.
    """
    text = prompt.lower()
    overrides: Dict[str, Any] = {}

    # 1. Detección de Escala
    scale = default_scale
    if any(k in text for k in ["gran escala", "parque", "monte", "iberdrola", "megavatio", "mw"]):
        scale = "large"
    elif any(k in text for k in ["mediano", "nave", "polideportivo", "industrial", "comercial"]):
        scale = "medium"
    elif any(k in text for k in ["doméstico", "domestico", "casa", "azotea", "tejado", "balcón", "balcon", "jardín", "huerto"]):
        scale = "domestic"

    # 2. Extracción de Números (Diámetro, Palas)
    # Diámetro en metros o mm
    diam_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:m(?:etros?)?)\b", text)
    diam_mm = re.search(r"(\d+(?:\.\d+)?)\s*mm\b", text)
    if diam_m and not diam_mm:
        val_m = float(diam_m.group(1))
        # Si el valor es razonable para metros (e.g. 0.5 a 60m)
        if val_m < 70.0:
            overrides["rotor_diameter"] = round(val_m * 1000.0, 1)
    elif diam_mm:
        overrides["rotor_diameter"] = float(diam_mm.group(1))

    # Número de palas
    blades = re.search(r"(\d+)\s*(?:palas?|álabes?|alabes?)", text)
    if blades:
        overrides["blade_count"] = max(2, min(8, int(blades.group(1))))

    # 3. Detección de Arquitectura Aerodinámica
    # Gorlov / Helicoidal
    if any(k in text for k in ["gorlov", "helicoid", "espiral", "torsion", "torsión", "silencio", "vibrac"]):
        family_id = "helical_gorlov"
    # Wind Lens / Carenado / Venturi / Difusor
    elif any(k in text for k in ["lens", "lente", "venturi", "difusor", "carenad", "embudo", "duct", "anillo"]):
        family_id = "wind_lens_ducted"
    # Híbrida Savonius - Darrieus
    elif any(k in text for k in ["hibrid", "híbrid", "darrieus", "doble etapa", "savonius-darrieus"]):
        family_id = "hybrid_savonius_darrieus"
    # Doble Rotor Contrarrotativo
    elif any(k in text for k in ["contrarrot", "doble rotor", "dos rotores", "tandem", "tándem", "crwt"]):
        family_id = "counter_rotating_crwt"
    # Bioinspirada (Tubérculos ballena)
    elif any(k in text for k in ["ballena", "bionic", "biónic", "biomimetic", "tuberculo", "tubérculo", "nodulo", "nódulo"]):
        family_id = "bionic_whale_tubercle"
    # Esférica
    elif any(k in text for k in ["esfer", "esfér", "cúpula", "cupula", "globo"]):
        family_id = "spherical_vawt"
    # Savonius clásico
    elif any(k in text for k in ["savonius", "arrastre puro", "media caña", "medio barril"]):
        family_id = "savonius_vawt"
    # HAWT clásico
    elif any(k in text for k in ["hawt", "horizontal", "molino", "hélice clásica"]):
        family_id = "hawt_conventional"
    # Inferencia por atributos físicos
    elif any(k in text for k in ["poco viento", "brisa", "arranque facil", "autoarranque"]):
        family_id = "wind_lens_ducted" if scale == "domestic" else "hybrid_savonius_darrieus"
    elif any(k in text for k in ["maxima potencia", "alta eficiencia", "recuperar estela"]):
        family_id = "counter_rotating_crwt"
    else:
        # Por defecto para exploración urbana avanzada: Gorlov Helicoidal
        family_id = "helical_gorlov"

    return family_id, scale, overrides


def build_synthesized_parameters(family_id: str, scale: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Genera el diccionario de parámetros paramétricos coherente con la escala."""
    params: Dict[str, Any] = {}

    if scale == "domestic":
        default_d = 900.0
        default_h = 1100.0
    elif scale == "medium":
        default_d = 2400.0
        default_h = 3200.0
    else:
        default_d = 32000.0
        default_h = 45000.0

    d_mm = overrides.get("rotor_diameter", default_d)
    # Respetar límites de escala si no se forzó un override explícito
    if "rotor_diameter" not in overrides:
        if scale == "domestic":
            d_mm = min(1300.0, max(400.0, d_mm))

    params["rotor_diameter"] = d_mm

    if family_id == "helical_gorlov":
        params["rotor_height"] = overrides.get("rotor_height", round(d_mm * 1.25, 1))
        params["blade_count"] = overrides.get("blade_count", 3)
        params["curvature_twist"] = 120.0
        params["blade_chord"] = round(d_mm * 0.15, 1)

    elif family_id == "wind_lens_ducted":
        params["blade_count"] = overrides.get("blade_count", 3)
        params["diffuser_length"] = round(d_mm * 0.35, 1)
        params["brim_height"] = round(d_mm * 0.08, 1)
        params["pitch_angle"] = 5.0
        params["tower_height"] = round(d_mm * 1.8, 1)

    elif family_id == "hybrid_savonius_darrieus":
        params["rotor_height"] = overrides.get("rotor_height", round(d_mm * 1.3, 1))
        params["blade_count"] = overrides.get("blade_count", 3)
        params["inner_diameter"] = round(d_mm * 0.45, 1)

    elif family_id == "counter_rotating_crwt":
        params["blade_count"] = overrides.get("blade_count", 3)
        params["rotor_spacing"] = round(d_mm * 0.35, 1)
        params["tower_height"] = round(d_mm * 1.8, 1)

    elif family_id == "bionic_whale_tubercle":
        params["blade_count"] = overrides.get("blade_count", 3)
        params["tubercle_count"] = 6
        params["tower_height"] = round(d_mm * 1.8, 1)
        params["pitch_angle"] = 6.0

    elif family_id == "spherical_vawt":
        params["blade_count"] = overrides.get("blade_count", 6)
        params["blade_thickness"] = 2.5 if scale == "domestic" else 4.5
        params["curvature_twist"] = 45.0

    elif family_id == "savonius_vawt":
        params["rotor_height"] = round(d_mm * 1.3, 1)
        params["blade_count"] = overrides.get("blade_count", 2)
        params["overlap_ratio"] = 0.18
        params["blade_thickness"] = 2.0 if scale == "domestic" else 4.0
        params["shaft_diameter"] = 25.0 if scale == "domestic" else 50.0

    else:
        # hawt_conventional
        params["blade_count"] = overrides.get("blade_count", 3)
        params["root_chord"] = round(d_mm * 0.08, 1)
        params["pitch_angle"] = 5.0
        params["tower_height"] = round(d_mm * 1.8, 1)

    return params


def generate_engineering_explanation(family_id: str, params: Dict[str, Any], metrics: Dict[str, Any], prompt: str) -> str:
    """Genera una explicación técnica y justificación física en español del diseño propuesto."""
    d_m = params.get("rotor_diameter", 1000.0) / 1000.0
    power = metrics.get("power_output", 0.0)
    cp = metrics.get("power_coefficient", 0.0)
    mass = metrics.get("rotor_mass", 0.0)
    torque = metrics.get("starting_torque", 0.0)

    if family_id == "helical_gorlov":
        return (
            f"Diseño sintetizado: Turbina Gorlov Helicoidal (Ø {d_m:.2f} m). "
            f"Las 3 palas helicoidales con torsión continua de {params.get('curvature_twist', 120)}° distribuyen el par motor homogéneamente en 360°, "
            f"eliminando las vibraciones pulsantes de las Darrieus convencionales y reduciendo el ruido en más de 8 dB. "
            f"Rendimiento estimado: {power:.1f} W (Cp={cp:.2f}), con una masa ligera de {mass:.1f} kg y par de arranque suave ({torque:.2f} N·m)."
        )

    elif family_id == "wind_lens_ducted":
        return (
            f"Diseño sintetizado: Turbina con Carenado Difusor Venturi / Wind Lens (Ø {d_m:.2f} m). "
            f"El anillo difusor con labio posterior (*brim*) genera vórtices toroidales de baja presión detrás del disco, "
            f"acelerando el flujo local en un factor ~1.35x. Esto multiplica la densidad de potencia efectiva alcanzando {power:.1f} W "
            f"con un Cp aparente de {cp:.2f}, ideal para arrancar y generar con brisas débiles en entornos residenciales."
        )

    elif family_id == "hybrid_savonius_darrieus":
        return (
            f"Diseño sintetizado: Turbina Híbrida Doble Etapa Savonius-Darrieus (Ø {d_m:.2f} m). "
            f"Combina un núcleo central de arrastre Savonius (autoarranque inmediato con alto par inicial de {torque:.2f} N·m) "
            f"con 3 palas aerodinámicas externas de sustentación que le permiten acelerar hasta TSR > 2.8 y generar {power:.1f} W (Cp={cp:.2f})."
        )

    elif family_id == "counter_rotating_crwt":
        return (
            f"Diseño sintetizado: Doble Rotor Coaxial Contrarrotativo CRWT (Ø {d_m:.2f} m). "
            f"El segundo rotor coaxial gira en sentido opuesto absorbiendo el torbellino de rotación de estela generado por el primero, "
            f"incrementando la eficiencia aerodinámica total hasta Cp={cp:.2f} y generando {power:.1f} W en un área frontal compacta."
        )

    elif family_id == "bionic_whale_tubercle":
        return (
            f"Diseño sintetizado: Rotor Bioinspirado con Tubérculos de Ballena Jorobada (Ø {d_m:.2f} m). "
            f"Las protuberancias sinusoidales en el borde de ataque inducen vórtices acoplados que retienen la capa límite adherida, "
            f"retrasando el ángulo de pérdida (*stall delay*) y manteniendo {power:.1f} W incluso bajo fuertes ráfagas y flujo turbulento."
        )

    else:
        return (
            f"Diseño sintetizado a partir de tu prompt: Diámetro {d_m:.2f} m, Potencia esperada: {power:.1f} W, "
            f"Rendimiento Cp: {cp:.2f}, Masa: {mass:.1f} kg. Configurado con restricciones físicas y aerodinámicas realistas."
        )


def format_top_code(family_id: str, scale: str, params: Dict[str, Any]) -> str:
    """Genera el código corto identificador para el Top (e.g. TOP-DOM-GORLOV-3P-900D)."""
    scale_prefix = "DOM" if scale == "domestic" else ("MED" if scale == "medium" else "GRAN")
    d_val = int(round(params.get("rotor_diameter", 1000.0)))

    type_code_map = {
        "helical_gorlov": "GORLOV",
        "wind_lens_ducted": "VENTURI",
        "hybrid_savonius_darrieus": "HIBRID",
        "counter_rotating_crwt": "CRWT",
        "bionic_whale_tubercle": "BIONIC",
        "spherical_vawt": "ESFR",
        "savonius_vawt": "SAVO",
        "hawt_conventional": "HAWT",
    }
    code_type = type_code_map.get(family_id, "GEN")
    blades = params.get("blade_count", 3)
    return f"TOP-{scale_prefix}-{code_type}-{blades}P-{d_val}D"
