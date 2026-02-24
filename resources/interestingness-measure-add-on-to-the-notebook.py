
# reformulation of next closure for interestingness measures
def NextClosureMeasure(ctx: pd.DataFrame, intent: t.Set, attribute_order: t.List, condition: t.Callable[[pd.DataFrame, t.Set], bool]) -> t.Set:
    intent = set(intent)
    for i, a in reversed(list(enumerate(attribute_order))): # For all i in M (in reversed order) do
        intent_b = intent.intersection(set(attribute_order[:i]))
        intent_b = downup(ctx, intent_b.union({a}))

        if LexicallyLower(intent, intent_b, attribute_order, i) and condition(ctx, intent): # added the condition here
            return intent_b
def AllClosureMeasureYield(ctx: pd.DataFrame, attribute_order: t.List, condition: t.Callable[[pd.DataFrame, t.Set], bool]) -> t.Generator[t.Set, None, None]:
    intent = downup(ctx, set())
    bottom = set(up(ctx, set()))
    
    while intent != bottom:
        yield intent
        intent = NextClosureMeasure(ctx, intent, attribute_order, condition)
    yield intent
def AllClosureMeasure(ctx: pd.DataFrame, attribute_order: t.List, condition: t.Callable[[pd.DataFrame, t.Set], bool]) -> t.List[t.Set]:
    return [intent for intent in AllClosureMeasureYield(ctx, attribute_order, condition)]
    

    
    
# Changes nothing to traditional AllClosure, because
def myInterestingnessMeasure(ctx: pd.DataFrame, intent: t.Set) -> bool:
    extent = set(down(ctx, intent))
    # do something
    return True

AllClosureMeasure(shapes, shapes.columns.to_list(), myInterestingnessMeasure)


# sometimes, for example with maxSupport, you need to force the appearance of top and/or bottom.
def NextClosureMeasure(ctx: pd.DataFrame, intent: t.Set, attribute_order: t.List, condition: t.Callable[[pd.DataFrame, t.Set], bool]) -> t.Set:
    intent = set(intent)
    for i, a in reversed(list(enumerate(attribute_order))): # For all i in M (in reversed order) do
        intent_b = intent.intersection(set(attribute_order[:i]))
        intent_b = downup(ctx, intent_b.union({a}))

        if LexicallyLower(intent, intent_b, attribute_order, i) and condition(ctx, intent): # added the condition here
            return intent_b
def AllClosureMeasureYield_Fixed(ctx: pd.DataFrame, attribute_order: t.List, condition: t.Callable[[pd.DataFrame, t.Set], bool]) -> t.Generator[t.Set, None, None]:
    intent = downup(ctx, set())
    bottom = set(up(ctx, set()))
    
    while intent != bottom and intent is not None: # in case the interestingness measure prevents from generating bottom, NextClosure will produce None, so we should stop
        yield intent
        intent = NextClosureMeasure(ctx, intent, attribute_order, condition)
    if intent is not None: # in case the interestingness measure prevents from generating bottom, NextClosure will produce None
        yield intent
def AllClosureMeasure_Fixed(ctx: pd.DataFrame, attribute_order: t.List, condition: t.Callable[[pd.DataFrame, t.Set], bool]) -> t.List[t.Set]:
    return [intent for intent in AllClosureMeasureYield(ctx, attribute_order, condition)]
