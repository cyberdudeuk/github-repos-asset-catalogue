"""Single source of the co-cddo snapshot time. Windows are date-based (UTC) so that 'last human commit within N days'
and 'commits in the last N days' always agree (defect R-1: epoch windows vs date-based ages disagreed at the boundary)."""
import os, datetime as dt
_S = os.path.dirname(os.path.abspath(__file__))
REF_EPOCH = int(open(os.path.join(_S, "ref_epoch.txt")).read().strip())
REF_DATE = dt.datetime.fromtimestamp(REF_EPOCH, dt.timezone.utc).date()
DAY = 86400
def cutoff(days):
    """Epoch of 00:00 UTC on REF_DATE - days. A commit counts in an N-day window iff its UTC date >= REF_DATE - N."""
    d = REF_DATE - dt.timedelta(days=days)
    return int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())
def days_since(epoch):
    return (REF_DATE - dt.datetime.fromtimestamp(epoch, dt.timezone.utc).date()).days if epoch else None
def status(last_human_epoch, last_any_epoch, archived):
    if not last_any_epoch: return "Empty"
    if archived: return "Archived"
    d = days_since(last_human_epoch)
    if d is None: return "Inactive"
    return "Active" if d <= 90 else "Maintained" if d <= 365 else "Dormant" if d <= 730 else "Inactive"
