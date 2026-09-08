"""Day 2 — CRDTs.

`test_replicas_converge_whatever_the_order` is the day, and it is the property the
whole family exists to provide.
"""

import random

import pytest

from crdt import GCounter, LWWRegister, PNCounter, RGA, TwoPhaseSet


# -- counters -----------------------------------------------------------------


def test_counters_merge_by_taking_the_maximum():
    """Not by adding. Merging the same state twice must not double anything, which
    is what makes the operation idempotent."""
    a = GCounter("a")
    b = GCounter("b")
    a.increment(3)
    b.increment(5)

    a.merge(b)
    a.merge(b)
    a.merge(b)
    assert a.value == 8


def test_merging_is_commutative():
    a, b = GCounter("a"), GCounter("b")
    a.increment(3)
    b.increment(5)

    forwards, backwards = GCounter("x"), GCounter("y")
    forwards.merge(a)
    forwards.merge(b)
    backwards.merge(b)
    backwards.merge(a)
    assert forwards.value == backwards.value


def test_a_g_counter_only_goes_up():
    with pytest.raises(ValueError):
        GCounter("a").increment(-1)


def test_a_pn_counter_goes_both_ways():
    counter = PNCounter("a")
    counter.increment(10)
    counter.decrement(3)
    assert counter.value == 7


def test_pn_counters_merge_correctly():
    a, b = PNCounter("a"), PNCounter("b")
    a.increment(10)
    a.decrement(2)
    b.increment(5)
    b.decrement(1)

    a.merge(b)
    assert a.value == 12


# -- sets ---------------------------------------------------------------------


def test_a_two_phase_set_adds_and_removes():
    s = TwoPhaseSet()
    s.add("x")
    assert "x" in s
    s.remove("x")
    assert "x" not in s


def test_a_removed_element_can_never_return():
    """The rule that makes the type converge, and the reason it is so often the
    wrong choice.

    Without it, an add and a remove arriving in different orders on two replicas
    would leave them disagreeing, and nothing could decide which is right.
    """
    s = TwoPhaseSet()
    s.add("x")
    s.remove("x")
    s.add("x")
    assert "x" not in s


def test_sets_converge_in_either_order():
    a, b = TwoPhaseSet(), TwoPhaseSet()
    a.add("x")
    a.add("y")
    b.add("x")
    b.remove("x")

    forwards, backwards = TwoPhaseSet(), TwoPhaseSet()
    forwards.merge(a)
    forwards.merge(b)
    backwards.merge(b)
    backwards.merge(a)
    assert forwards.elements() == backwards.elements() == {"y"}


# -- registers ----------------------------------------------------------------


def test_the_later_causal_write_wins():
    a, b = LWWRegister("a"), LWWRegister("b")
    a.set("first")
    b.merge(a)
    b.set("second")
    a.merge(b)
    assert a.value == "second"


def test_a_slow_clock_cannot_lose_a_race_it_should_have_won():
    """Week 5's clock-skew problem, avoided rather than tolerated. The clock is a
    counter over what has been *seen*, so 'later' means 'knew about the earlier
    one' — and no machine's wall clock is involved at all."""
    fast, slow = LWWRegister("fast"), LWWRegister("slow")
    for _ in range(100):
        fast.set("noise")            # a chatty node, high counter

    slow.merge(fast)
    slow.set("the real update")      # written after seeing everything

    fast.merge(slow)
    assert fast.value == "the real update"


def test_registers_converge_either_way():
    a, b = LWWRegister("a"), LWWRegister("b")
    a.set(1)
    b.set(2)

    forwards, backwards = LWWRegister("f"), LWWRegister("g")
    forwards.merge(a)
    forwards.merge(b)
    backwards.merge(b)
    backwards.merge(a)
    assert forwards.value == backwards.value


# -- the sequence -------------------------------------------------------------


def build(text: str) -> tuple[RGA, list]:
    doc = RGA("a")
    ids, previous = [], None
    for char in text:
        previous = doc.insert_after(previous, char)
        ids.append(previous)
    return doc, ids


def test_text_reads_back():
    doc, _ids = build("HELLO")
    assert doc.text() == "HELLO"


def test_inserting_at_the_front():
    doc, _ids = build("ELLO")
    doc.insert_after(None, "H")
    assert doc.text() == "HELLO"


def test_a_delete_is_a_tombstone():
    doc, ids = build("HELLO")
    doc.delete(ids[4])
    assert doc.text() == "HELL"
    assert ids[4] in doc.elements, "the element is still there, it just stops rendering"


def test_the_article_example():
    """Ana inserts at the front, Bo deletes the last character, concurrently.

    Apply the raw operations naively and you get two different documents with no
    error. Here both sides arrive at the same one, and neither needed to know what
    the other was doing.
    """
    original, ids = build("HELLO")
    ana, bo = RGA("ana"), RGA("bo")
    ana.merge(original)
    bo.merge(original)

    ana.insert_after(None, "X")
    bo.delete(ids[4])

    ana_final, bo_final = RGA("f"), RGA("g")
    ana_final.merge(ana)
    ana_final.merge(bo)
    bo_final.merge(bo)
    bo_final.merge(ana)

    assert ana_final.text() == bo_final.text() == "XHELL"


@pytest.mark.parametrize("seed", range(20))
def test_replicas_converge_whatever_the_order(seed):
    """The property the whole family exists to provide.

    Two replicas make five concurrent edits each, at random positions, knowing
    nothing about each other. Merged in either order, the documents are identical.

    No transformation function, no central server, and no requirement that
    anything arrive in any particular order.
    """
    rng = random.Random(seed)
    base, _ids = build("abc")

    left, right = RGA("left"), RGA("right")
    left.merge(base)
    right.merge(base)

    for doc, char in ((left, "X"), (right, "Y")):
        for _ in range(5):
            anchor = rng.choice([None] + list(doc.elements))
            doc.insert_after(anchor, char)

    forwards, backwards = RGA("f"), RGA("g")
    forwards.merge(left)
    forwards.merge(right)
    backwards.merge(right)
    backwards.merge(left)

    assert forwards.text() == backwards.text()


def test_merging_is_idempotent():
    left, _ids = build("abc")
    right = RGA("right")
    right.merge(left)
    before = right.text()
    right.merge(left)
    right.merge(left)
    assert right.text() == before


def test_convergence_is_not_correctness():
    """The honest limit of the whole family.

    Two people insert incompatible text at the same point. The replicas converge —
    they agree completely — and the result is nonsense. **Everyone sees the same
    nonsense**, and no algorithm decides which intention should have won.
    """
    base, ids = build("cat")
    left, right = RGA("left"), RGA("right")
    left.merge(base)
    right.merge(base)

    left.insert_after(ids[0], "X")
    right.insert_after(ids[0], "Y")

    merged_left, merged_right = RGA("a"), RGA("b")
    merged_left.merge(left)
    merged_left.merge(right)
    merged_right.merge(right)
    merged_right.merge(left)

    assert merged_left.text() == merged_right.text()
    assert merged_left.text() not in ("cXat", "cYat"), "neither intention survived intact"
