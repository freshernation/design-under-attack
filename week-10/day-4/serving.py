"""Serving a model, and serving media. Two expensive resources, two designs
arranged around not wasting them.

The batching figures here are a **stipulated model**, as in week 3 and week 9. The
tests assert the direction of each effect, never its magnitude.

Replace each `raise NotImplementedError` with your own code.
"""

import math


def static_batch_utilisation(lengths: list[int]) -> float:
    """Accelerator utilisation when a batch runs to completion together, to four
    decimals.

    The batch takes as long as its longest member, so every slot that finished
    early is idle for the rest of it:

        sum(lengths) / (len(lengths) * max(lengths))

    Raises ValueError for an empty batch.
    """
    raise NotImplementedError


def continuous_batch_utilisation(lengths: list[int], queue_depth: int) -> float:
    """The same batch, with finished slots refilled from a queue, to four decimals.

    A slot that finishes early is immediately given the next queued request, so
    the idle time is filled — as long as there is something to fill it with. With
    a queue at least as deep as the batch, utilisation is 1.0.

    Model the partial case as the static utilisation plus the fraction of idle
    slot-time that the queue can cover.
    """
    raise NotImplementedError


def tokens_per_second(batch_size: int, ms_per_step: float) -> float:
    """Throughput: one step produces one token for every sequence in the batch.

    Raises ValueError for a non-positive batch or step time.
    """
    raise NotImplementedError


def capacity_in_requests(tokens_per_second_value: float, mean_tokens_per_request: float) -> float:
    """Requests per second, to two decimals — **and the number not to plan with.**

    A capacity in requests is a capacity at one particular length distribution. The
    moment the distribution moves, it is wrong, and it moves whenever the product
    changes. Plan in tokens.
    """
    raise NotImplementedError


def time_to_first_token_ms(queued_tokens: float, tokens_per_second_value: float) -> float:
    """How long a request waits before anything appears, to one decimal.

    One of the two latency objectives, and the one users experience as "is it
    broken?". The other is the gap between subsequent tokens, which they
    experience as "is it slow?" — and averaging the two describes neither.
    """
    raise NotImplementedError


def admission_by_tokens(queued_tokens: float, budget_tokens: float) -> bool:
    """Whether to accept another request.

    Admission by **requests in flight** is wrong here: one request can be a
    hundred times another. The queue is measured in tokens because that is what it
    actually costs.
    """
    raise NotImplementedError


def egress_cost(bytes_served: float, cost_per_gb: float, edge_fraction: float) -> float:
    """Monthly egress cost, to two decimals, where `edge_fraction` is served from
    inside the viewer's network and costs nothing.

    For most systems bandwidth is a line item. For video it is the bill, and a
    percentage point of edge coverage is a large number.

    Raises ValueError for an edge fraction outside [0, 1].
    """
    raise NotImplementedError
