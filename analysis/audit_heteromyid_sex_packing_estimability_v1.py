from __future__ import annotations


def _qualifying_species(
    inventory: dict,
    *,
    source: str,
) -> list[str]:
    out=[]
    for species,row in sorted((inventory.get("species") or {}).items()):
        paired=int(row.get("paired_n3_sessions",0) or 0)
        if paired < 10:
            continue
        if source=="Portal":
            if int(row.get("independent_plots",0) or 0) < 2:
                continue
        elif source=="NEON":
            if int(row.get("independent_sites",0) or 0) < 2:
                continue
        else:
            raise ValueError(f"unknown source {source}")
        out.append(species)
    return out


def evaluate_gate(portal_inventory: dict, neon_inventory: dict) -> dict:
    portal=_qualifying_species(portal_inventory,source="Portal")
    neon=_qualifying_species(neon_inventory,source="NEON")

    portal_counts={
        species:int((portal_inventory.get("species") or {}).get(species,{}).get("paired_n3_sessions",0) or 0)
        for species in portal_inventory.get("species",{})
    }
    neon_counts={
        species:int((neon_inventory.get("species") or {}).get(species,{}).get("paired_n3_sessions",0) or 0)
        for species in neon_inventory.get("species",{})
    }
    shared=sorted(
        species
        for species in set(portal_counts)&set(neon_counts)
        if portal_counts[species]>=10 and neon_counts[species]>=10
    )

    portal_pass=len(portal)>=3
    neon_pass=len(neon)>=3
    return {
        "portal_family_qualifying_species":portal,
        "neon_family_qualifying_species":neon,
        "portal_family_gate_passed":portal_pass,
        "neon_family_gate_passed":neon_pass,
        "shared_species_with_ge10_paired_n3_sessions":shared,
        "effect_modeling_authorized":portal_pass or neon_pass,
        "cross_source_headline_authorized":portal_pass and neon_pass and bool(shared),
        "ecological_effects_inspected":False,
    }
