"""
Template Processor for Kometa Web UI

Simplified template processing for overlay preview.
This handles the most common template patterns used in Kometa overlay files
without the full complexity of the main Kometa template engine.
"""

import re
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


class TemplateProcessor:
    """Processes Kometa templates for overlay preview."""

    def __init__(self, kometa_root: Path):
        self.kometa_root = Path(kometa_root)
        self.defaults_dir = self.kometa_root / "defaults" / "overlays"
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self._template_cache: Dict[str, Dict] = {}

    def load_templates(self, template_source: str = "templates") -> Dict[str, Any]:
        """Load templates from a template file."""
        if template_source in self._template_cache:
            return self._template_cache[template_source]

        # Handle 'default: templates' which refers to templates.yml in the same directory
        if template_source == "templates":
            template_path = self.defaults_dir / "templates.yml"
        else:
            template_path = Path(template_source)
            if not template_path.is_absolute():
                template_path = self.defaults_dir / template_source

        if not template_path.exists():
            return {}

        try:
            with open(template_path, encoding="utf-8") as f:
                data = self.yaml.load(f)
            templates = data.get("templates", {}) if data else {}
            self._template_cache[template_source] = templates
            return templates
        except Exception as e:
            print(f"Failed to load templates from {template_path}: {e}")
            return {}

    def resolve_variable(self, value: Any, variables: Dict[str, Any], max_depth: int = 10) -> Any:
        """
        Resolve <<variable>> placeholders in a value.

        Handles nested variable references like <<rating<<rating_num>>_font>>:
        - First pass: resolve inner variable -> <<rating1_font>>
        - Second pass: resolve outer variable -> actual font value
        """
        if value is None:
            return None

        if isinstance(value, str):
            result = value

            # Iteratively resolve nested variables (up to max_depth iterations)
            for _ in range(max_depth):
                prev_result = result

                # First, resolve inner nested variables
                # Pattern matches nested variables like <<rating<<rating_num>>_font>>
                # We need to resolve from innermost out
                while True:
                    # Find innermost variable references (those without << inside them)
                    innermost_pattern = r'<<([^<>]+)>>'
                    matches = list(re.finditer(innermost_pattern, result))
                    if not matches:
                        break

                    made_replacement = False
                    for match in matches:
                        var_name = match.group(1)
                        placeholder = f"<<{var_name}>>"

                        if var_name in variables and variables[var_name] is not None:
                            var_value = variables[var_name]
                            if result == placeholder:
                                # Entire value is the variable - return as-is for type preservation
                                return var_value
                            else:
                                # Variable is part of a larger string
                                result = result.replace(placeholder, str(var_value))
                                made_replacement = True

                    if not made_replacement:
                        break

                # If nothing changed, we're done
                if result == prev_result:
                    break

            return result

        elif isinstance(value, dict):
            return {k: self.resolve_variable(v, variables) for k, v in value.items()}

        elif isinstance(value, list):
            return [self.resolve_variable(item, variables) for item in value]

        return value

    def evaluate_conditionals(
        self,
        conditionals: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate conditional expressions and return resolved values."""
        results = {}

        for cond_name, cond_def in conditionals.items():
            if not isinstance(cond_def, dict):
                continue

            # Resolve variables in the conditional name itself (e.g., rating<<rating_num>>_horizontal_align)
            resolved_cond_name = self.resolve_variable(cond_name, variables)
            if isinstance(resolved_cond_name, str):
                cond_name = resolved_cond_name

            default_value = cond_def.get("default")
            conditions = cond_def.get("conditions", [])

            if isinstance(conditions, dict):
                conditions = [conditions]

            resolved_value = default_value
            for condition in conditions:
                if not isinstance(condition, dict):
                    continue

                condition_value = condition.get("value")
                condition_met = True

                for check_key, check_value in condition.items():
                    if check_key == "value":
                        continue

                    # Resolve variables in the check key (e.g., rating<<rating_num>>_image)
                    resolved_check_key = self.resolve_variable(check_key, variables)
                    if isinstance(resolved_check_key, str):
                        check_key = resolved_check_key

                    # Handle .exists checks
                    if check_key.endswith(".exists"):
                        var_name = check_key[:-7]
                        # Also resolve variables in the var_name for .exists checks
                        resolved_var_name = self.resolve_variable(var_name, variables)
                        if isinstance(resolved_var_name, str):
                            var_name = resolved_var_name

                        # A variable "exists" if:
                        # 1. It's in the variables dict
                        # 2. Its value is not None
                        # 3. Its value is not an unresolved placeholder (like <<file>>)
                        var_value = variables.get(var_name)
                        var_exists = var_value is not None
                        if var_exists and isinstance(var_value, str) and "<<" in var_value and ">>" in var_value:
                            # Value is an unresolved placeholder - treat as non-existent
                            var_exists = False

                        expected = check_value if isinstance(check_value, bool) else str(check_value).lower() == "true"
                        if var_exists != expected:
                            condition_met = False
                            break

                    # Handle .not checks
                    elif check_key.endswith(".not"):
                        var_name = check_key[:-4]
                        if var_name in variables:
                            var_val = variables[var_name]
                            if isinstance(check_value, list):
                                if var_val in check_value:
                                    condition_met = False
                                    break
                            elif str(var_val) == str(check_value):
                                condition_met = False
                                break

                    # Standard equality check
                    elif check_key in variables:
                        var_val = variables[check_key]
                        if isinstance(check_value, list):
                            if var_val not in check_value:
                                condition_met = False
                                break
                        elif str(var_val) != str(check_value):
                            condition_met = False
                            break
                    else:
                        # Variable doesn't exist, condition fails
                        condition_met = False
                        break

                if condition_met:
                    resolved_value = condition_value
                    break

            # Resolve any variables in the result
            final_value = self.resolve_variable(resolved_value, variables)
            results[cond_name] = final_value

        return results

    def process_template(
        self,
        template_name: str,
        template_def: Dict[str, Any],
        user_variables: Dict[str, Any],
        key: str = ""
    ) -> Dict[str, Any]:
        """
        Process a single template with user-provided variables.

        Handles complex templates like 'ratings' which use nested variable references
        such as <<rating<<rating_num>>_font>> where rating_num is substituted first.
        """
        # Start with user variables (these should be available for resolving defaults)
        variables = dict(user_variables)

        # Add 'key' variable which is commonly used
        variables["key"] = key


        # Process template defaults - resolve keys using variables (which now include user_variables)
        if "default" in template_def and isinstance(template_def["default"], dict):
            for dk, dv in template_def["default"].items():
                # Resolve nested keys first (like rating<<rating_num>>_file becomes rating1_file)
                resolved_key = self.resolve_variable(dk, variables)
                # Only set if not already provided by user
                if resolved_key not in variables:
                    variables[resolved_key] = dv

        # Now do multiple passes to resolve all nested variables in the variable values
        for _ in range(5):  # Multiple passes to handle nested dependencies
            prev_vars = dict(variables)
            for vk, vv in list(variables.items()):
                if isinstance(vv, str) and "<<" in vv:
                    resolved = self.resolve_variable(vv, variables)
                    variables[vk] = resolved
            # Also re-resolve keys that may have had nested variable references
            resolved_vars = {}
            for vk, vv in list(variables.items()):
                if isinstance(vk, str) and "<<" in vk:
                    resolved_key = self.resolve_variable(vk, variables)
                    if resolved_key != vk:
                        resolved_vars[resolved_key] = vv
                else:
                    resolved_vars[vk] = vv
            variables = resolved_vars
            if variables == prev_vars:
                break


        # Process conditionals with resolved variables
        if "conditionals" in template_def and isinstance(template_def["conditionals"], dict):
            conditional_results = self.evaluate_conditionals(template_def["conditionals"], variables)
            variables.update(conditional_results)


        # Re-process template defaults now that conditionals have added new values
        # This handles cases like pmm_<<key>>: <<default>> where default is set by conditional
        if "default" in template_def and isinstance(template_def["default"], dict):
            for dk, dv in template_def["default"].items():
                resolved_key = self.resolve_variable(dk, variables)
                # Re-resolve value using updated variables (including conditional results)
                if isinstance(dv, str) and "<<" in dv:
                    resolved_value = self.resolve_variable(dv, variables)
                    # Update if value was previously unresolved but now can be resolved
                    if resolved_value is not None and (
                        resolved_key not in variables or
                        variables.get(resolved_key) is None or
                        (isinstance(variables.get(resolved_key), str) and "<<" in str(variables.get(resolved_key)))
                    ):
                        variables[resolved_key] = resolved_value

        # Do another pass after conditionals and re-processed defaults
        for _ in range(5):  # More passes to handle longer chains
            prev_vars = dict(variables)
            for vk, vv in list(variables.items()):
                if isinstance(vv, str) and "<<" in vv:
                    resolved = self.resolve_variable(vv, variables)
                    variables[vk] = resolved
            if variables == prev_vars:
                break


        # Now resolve the overlay configuration
        overlay_def = template_def.get("overlay", {})
        if not overlay_def:
            return {}

        resolved_overlay = {}
        for ok, ov in overlay_def.items():
            resolved_key = self.resolve_variable(ok, variables)
            resolved_value = self.resolve_variable(ov, variables)
            # For name field, keep even if it has unresolved variables (for text overlays)
            # Other fields skip if still unresolved
            if ok == "name":
                if resolved_value is not None:
                    resolved_overlay[resolved_key] = resolved_value
            elif resolved_value is not None and not (isinstance(resolved_value, str) and "<<" in resolved_value):
                resolved_overlay[resolved_key] = resolved_value

        return resolved_overlay

    def preprocess_template_variables(
        self,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Preprocess user template variables to expand shorthand notations.

        Handles rating shorthand like "rating1: user / rt_tomato" which expands to:
          - rating1: user
          - rating1_image: rt_tomato
        """
        result = dict(variables)

        # Process rating shorthand for rating1, rating2, rating3
        for i in range(1, 4):
            key = f"rating{i}"
            if key in result and isinstance(result[key], str):
                value = result[key]
                # Check for shorthand format: "type / image"
                if " / " in value:
                    parts = [p.strip() for p in value.split(" / ", 1)]
                    if len(parts) == 2:
                        rating_type, rating_image = parts
                        result[key] = rating_type
                        result[f"{key}_image"] = rating_image
                        logger.info("Expanded %s: '%s' -> %s='%s', %s_image='%s'",
                                    key, value, key, rating_type, key, rating_image)

        return result

    def _extract_external_template_vars(
        self,
        ext_tmpl: Dict[str, Any],
        key: str = ""
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract variables and conditionals from external_templates.template_variables.

        The template_variables section can contain:
        - 'default': a dict of default values for variables
        - 'conditionals': a dict of conditional definitions
        - Other keys: scalar template variables

        Returns (variables, conditionals) tuple.
        """
        variables = {}
        conditionals = {}

        if "template_variables" not in ext_tmpl:
            return variables, conditionals

        tmpl_vars = ext_tmpl["template_variables"]
        if not isinstance(tmpl_vars, dict):
            return variables, conditionals

        for tk, tv in tmpl_vars.items():
            if tk == "default" and isinstance(tv, dict):
                # This is a dict of default values for other variables
                for dk, dv in tv.items():
                    if dk not in variables:
                        variables[dk] = dv
            elif tk == "conditionals" and isinstance(tv, dict):
                # These are conditional definitions to be processed later
                conditionals.update(tv)
            else:
                # Regular template variable
                variables[tk] = tv

        return variables, conditionals

    def expand_overlay_file(
        self,
        file_path: str,
        user_template_variables: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Expand an overlay file, processing all templates and returning
        a list of fully resolved overlay configurations.
        """
        path = Path(file_path)
        if not path.exists():
            return []

        try:
            with open(path, encoding="utf-8") as f:
                data = self.yaml.load(f)
        except Exception as e:
            print(f"Failed to load overlay file {file_path}: {e}")
            return []

        if not data:
            return []

        # Preprocess user variables to expand shorthand notations
        user_vars = self.preprocess_template_variables(user_template_variables or {})
        expanded_overlays = []

        # Load external templates if specified
        external_templates = {}
        external_conditionals = {}
        if "external_templates" in data:
            ext_tmpl = data["external_templates"]
            if isinstance(ext_tmpl, dict):
                template_source = ext_tmpl.get("default", "templates")
                external_templates = self.load_templates(template_source)

                # Extract variables and conditionals from template_variables
                ext_vars, ext_conds = self._extract_external_template_vars(ext_tmpl)
                # Apply external vars as defaults (user vars take precedence)
                for ek, ev in ext_vars.items():
                    if ek not in user_vars:
                        user_vars[ek] = ev
                external_conditionals = ext_conds

        # Load local templates
        local_templates = data.get("templates", {})

        # Combine templates (local takes precedence)
        all_templates = {**external_templates, **local_templates}

        # Process each overlay
        overlays_section = data.get("overlays", {})
        for overlay_name, overlay_def in overlays_section.items():
            if not isinstance(overlay_def, dict):
                continue

            # Check if this overlay uses a template
            if "template" in overlay_def:
                template_call = overlay_def["template"]
                template_calls = template_call if isinstance(template_call, list) else [template_call]

                # Start with user vars
                overlay_vars = dict(user_vars)

                # Add overlay-level variables (Kometa uses 'variables' key)
                if "variables" in overlay_def and isinstance(overlay_def["variables"], dict):
                    overlay_vars.update(overlay_def["variables"])

                # Also check for template_variables (alternative key)
                if "template_variables" in overlay_def and isinstance(overlay_def["template_variables"], dict):
                    overlay_vars.update(overlay_def["template_variables"])

                # Extract key from overlay name for variable substitution
                # For "Dolby-TrueHD-Atmos", if variables has 'key', use that
                # Otherwise extract from name
                if "key" not in overlay_vars:
                    overlay_vars["key"] = overlay_name.split("-")[-1] if "-" in overlay_name else overlay_name

                # Process all templates in sequence, merging results
                merged_overlay = {}
                for tmpl_call in template_calls:
                    if isinstance(tmpl_call, dict):
                        tmpl_name = tmpl_call.get("name", "standard")
                        tmpl_vars = {k: v for k, v in tmpl_call.items() if k != "name"}
                    elif isinstance(tmpl_call, str):
                        tmpl_name = tmpl_call
                        tmpl_vars = {}
                    else:
                        continue

                    if tmpl_name not in all_templates:
                        continue

                    template_def = all_templates[tmpl_name]
                    if isinstance(template_def, list) and len(template_def) > 0:
                        template_def = template_def[0]

                    # Create a copy of template_def that includes external conditionals
                    effective_template = dict(template_def) if isinstance(template_def, dict) else {}
                    if external_conditionals:
                        if "conditionals" in effective_template:
                            # Merge: external conditionals are defaults, template ones override
                            merged_conds = dict(external_conditionals)
                            merged_conds.update(effective_template["conditionals"])
                            effective_template["conditionals"] = merged_conds
                        else:
                            effective_template["conditionals"] = external_conditionals


                    # Combine variables: overlay_vars + template call vars
                    combined_vars = {**overlay_vars, **tmpl_vars}

                    resolved = self.process_template(tmpl_name, effective_template, combined_vars, combined_vars.get("key", ""))
                    if resolved:
                        # Merge into the combined result (later templates override earlier)
                        for rk, rv in resolved.items():
                            if not rk.startswith("_") and rv is not None:
                                merged_overlay[rk] = rv

                if merged_overlay:
                    merged_overlay["_original_name"] = overlay_name
                    merged_overlay["_template"] = ", ".join(
                        tmpl_call.get("name", tmpl_call) if isinstance(tmpl_call, dict) else str(tmpl_call)
                        for tmpl_call in template_calls
                    )
                    expanded_overlays.append(merged_overlay)
                    logger.debug("Expanded overlay '%s' with template(s): name=%s, default=%s",
                                 overlay_name, merged_overlay.get("name"), merged_overlay.get("default"))

            # Direct overlay definition (no template)
            elif "overlay" in overlay_def:
                overlay_config = overlay_def["overlay"]
                if isinstance(overlay_config, dict):
                    # Resolve any variables in the direct definition
                    resolved = {}
                    for ok, ov in overlay_config.items():
                        resolved_value = self.resolve_variable(ov, user_vars)
                        if resolved_value is not None:
                            resolved[ok] = resolved_value

                    resolved["_original_name"] = overlay_name
                    resolved["_direct"] = True
                    expanded_overlays.append(resolved)

        return expanded_overlays

    def get_overlay_keys_from_file(self, file_path: str) -> List[str]:
        """Get all overlay keys/names from a file without full expansion."""
        path = Path(file_path)
        if not path.exists():
            return []

        try:
            with open(path, encoding="utf-8") as f:
                data = self.yaml.load(f)
        except Exception:
            return []

        if not data or "overlays" not in data:
            return []

        return list(data["overlays"].keys())
