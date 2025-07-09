from datetime import datetime, timedelta

def compute_next_scans(next_scan_date_, scan_interval):
    """
    Calcule la date du prochain scan et du scan suivant.
    next_scan_date_ : str (ISO ou '%Y-%m-%d %H:%M:%S') ou datetime
    scan_interval : int (secondes)
    Retourne (prochain_scan, scan_suivant) ou (None, None) si erreur.
    """
    if not next_scan_date_ or not scan_interval:
        return None, None
    try:
        dt = next_scan_date_
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except Exception:
                dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        prochain_scan = dt + timedelta(seconds=int(scan_interval))
        scan_suivant = prochain_scan + timedelta(seconds=int(scan_interval))
        return prochain_scan, scan_suivant
    except Exception:
        return None, None 