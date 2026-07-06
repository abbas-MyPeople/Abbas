"""
Clover adapter for az-social-tables — MOCKED. No network calls in this module.

Purpose: define the contract for how event-night ROI will eventually be measured
straight from the restaurant's POS, so app.py codes against a stable interface
today and the real client drops in later without touching anything else.

The real implementation will mirror the proven read-only pattern in the sister
repo (WokAndKarahiTexas.com/clover-analysis/clover_client.py):
  - stdlib urllib GETs against https://api.clover.com/v3/merchants/{MID}
  - env vars CLOVER_API_TOKEN + CLOVER_MERCHANT_ID from a gitignored .env
  - orders pulled by createdTime window with
    expand=lineItems,orderType,payments,customers
  - STRICTLY read-only: never POST/PUT/DELETE.

Baseline definition (see PRODUCT_SPEC): for an event window, the baseline is the
average revenue of the same weekday + same time window over the previous 4 weeks.
Incremental revenue = event-window revenue − baseline. That definition is encoded
here so the mock and the future real adapter agree.
"""

import os


class CloverAdapterBase:
    """Contract every adapter (mock now, real later) must satisfy."""

    def sales_by_window(self, date, start_time, end_time):
        """Total gross sales (USD) between start_time and end_time on date.

        Real impl: sum payments on orders filtered by createdTime within the
        window (ms epoch), excluding refunds/voids.
        """
        raise NotImplementedError

    def baseline_for_window(self, date, start_time, end_time, weeks=4):
        """Average same-weekday, same-window sales over the prior `weeks` weeks."""
        raise NotImplementedError

    def event_night_report(self, date, start_time, end_time):
        """Event revenue vs baseline → dict with revenue, baseline, incremental."""
        revenue = self.sales_by_window(date, start_time, end_time)
        baseline = self.baseline_for_window(date, start_time, end_time)
        return {
            "date": date,
            "window": f"{start_time}-{end_time}",
            "revenue": revenue,
            "baseline": baseline,
            "incremental": round(revenue - baseline, 2),
            "source": self.source,
        }

    def guest_checkins(self, date):
        """Future: correlate host check-ins with Clover orders/customers to
        attribute spend per seated guest. Clover 'customers' expansion + order
        notes are the likely hooks; may stay manual if attribution is noisy."""
        raise NotImplementedError


class MockCloverAdapter(CloverAdapterBase):
    """Deterministic fake numbers so the admin ROI panel renders during the
    pilot. The operator's manually-entered estimates always take precedence in
    app.py; this exists to exercise the interface end-to-end."""

    source = "mock"

    # Plausible slow-weeknight dinner-window revenue for a small restaurant.
    _BASELINE = 420.0

    def sales_by_window(self, date, start_time, end_time):
        # Deterministic per-date variation (no randomness — reproducible demos).
        bump = (sum(ord(c) for c in date) % 9) * 35
        return round(self._BASELINE + 180 + bump, 2)

    def baseline_for_window(self, date, start_time, end_time, weeks=4):
        return self._BASELINE

    def guest_checkins(self, date):
        return []


def get_adapter():
    """Mock unless a real adapter is explicitly wired in later.

    When the real client lands, this will return it only when CLOVER_API_TOKEN
    and CLOVER_MERCHANT_ID are present (never committed — see .env.example).
    """
    if os.environ.get("AZST_CLOVER_MODE", "mock") == "real":
        raise NotImplementedError(
            "Real Clover adapter not built yet — pilot runs on manual estimates "
            "+ the mock. See this module's docstring for the implementation plan."
        )
    return MockCloverAdapter()
