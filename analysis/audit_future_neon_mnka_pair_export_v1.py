"""Export prospective genus-MNKA predictor sessions without spatial response data.

All session inclusion rules are copied from frozen structural gate.
Only event identity/date and genotype-independent genus MNKA are exported.
No tags, trap coordinates, W, B, NN or abundance-response slopes.
"""
def future_mnka_predictor_pairs(sessions, event_metadata, mnka_map, targets):
    out=[]
    for s in sessions:
        if not s.get("primary_complete_session") or s.get("taxon") not in targets:
            continue
        if int(s.get("n_repeat_coordinate_supported_tagged_individuals",0))<5:
            continue
        if float(s.get("all_capture_trap_night_fraction_of_observed",1.))>.30:
            continue
        if len(s.get("site_ids",[]))!=1 or len(s.get("genus_labels",[]))!=1:
            continue
        site=s["site_ids"][0];genus=s["genus_labels"][0]
        key=(site,s["plot_id"],s["event_id"])
        data=event_metadata.get(key)
        if not data:raise RuntimeError("eligible response event missing date metadata")
        mnka=mnka_map.get((site,s["plot_id"],s["event_id"],genus))
        if mnka is None:
            raise RuntimeError("eligible response lacks continuous historical MNKA")
        out.append({
            "taxon":s["taxon"],"genus":genus,
            "site":site,"plot_id":s["plot_id"],"event_id":s["event_id"],
            "date":data["date"].isoformat(),
            "genus_mnka":int(mnka),
            "frozen_repeat_supported_m":int(
                s["n_repeat_coordinate_supported_tagged_individuals"]),
            "frozen_trap_saturation":float(
                s["all_capture_trap_night_fraction_of_observed"]),
        })
    keys=[(r["taxon"],r["site"],r["plot_id"],r["event_id"]) for r in out]
    if len(keys)!=len(set(keys)):
        raise RuntimeError("duplicate released future event taxon response identity")
    if len(out)!=287:
        raise RuntimeError(f"future predictor cohort drifted: {len(out)} != 287")
    return sorted(out,key=lambda r:(r["site"],r["plot_id"],r["event_id"],r["taxon"]))
