from datetime import date, datetime
from typing import Generator, Optional

import pendulum  # type: ignore


def month_range(
    start: date, to: Optional[date] = None
) -> Generator[date, None, None]:
    start_month = (
        pendulum.instance(datetime(start.year, start.month, start.day))
        .start_of("month")
        .date()
    )
    end_month = pendulum.instance(datetime.today()).start_of("month").date()
    if to:
        end_month = (
            pendulum.instance(datetime(to.year, to.month, to.day))
            .start_of("month")
            .date()
        )

    if end_month < start_month:
        raise ValueError("to must be later than start")

    current_month = start_month
    while current_month <= end_month:
        yield current_month

        current_month = current_month.add(months=1)
