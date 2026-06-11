@Test(timeout = 4000)
    public void testNotNullPredicateCreation() throws Throwable {
        // Given: A NOT_NULL ObjectPredicate
        Predicates.ObjectPredicate notNullPredicate = Predicates.ObjectPredicate.NOT_NULL;

        // When: Creating a narrowed type predicate
        Predicate<Predicates.ObjectPredicate> predicate = notNullPredicate.withNarrowedType();

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testIsNullPredicateCreation() throws Throwable {
        // When: Creating an isNull predicate
        Predicate<Predicates.ObjectPredicate> predicate = Predicates.isNull();

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testInPredicateWithEmptyCollection() throws Throwable {
        // Given: An empty collection and a NOT_NULL ObjectPredicate
        Predicates.ObjectPredicate notNullPredicate = Predicates.ObjectPredicate.NOT_NULL;
        ArrayList<Predicates.ObjectPredicate> collection = new ArrayList<>();

        // When: Creating an in predicate and testing removal
        Predicate<Predicates.ObjectPredicate> inPredicate = Predicates.in(collection);
        java.util.function.Predicate<Predicates.ObjectPredicate> isEqualPredicate = java.util.function.Predicate.isEqual(inPredicate);
        collection.add(notNullPredicate);
        boolean removed = collection.removeIf(isEqualPredicate);

        // Then: The collection should still contain the NOT_NULL predicate and nothing should be removed
        assertTrue("Collection should contain NOT_NULL predicate", collection.contains(notNullPredicate));
        assertFalse("Nothing should be removed", removed);
    }

    @Test(timeout = 4000)
    public void testInstanceOfPredicateWithNonMatchingType() throws Throwable {
        // Given: A NOT_NULL ObjectPredicate and a class type
        Predicates.ObjectPredicate notNullPredicate = Predicates.ObjectPredicate.NOT_NULL;
        Class<CharMatcher> charMatcherClass = CharMatcher.class;

        // When: Creating an instanceOf predicate and testing removal
        Predicate<Object> instanceOfPredicate = Predicates.instanceOf(charMatcherClass);
        ArrayList<Predicates.ObjectPredicate> collection = new ArrayList<>();
        java.util.function.Predicate<Predicates.ObjectPredicate> isEqualPredicate = java.util.function.Predicate.isEqual(instanceOfPredicate);
        collection.add(notNullPredicate);
        boolean removed = collection.removeIf(isEqualPredicate);

        // Then: The collection should still contain the NOT_NULL predicate and nothing should be removed
        assertTrue("Collection should contain NOT_NULL predicate", collection.contains(notNullPredicate));
        assertFalse("Nothing should be removed", removed);
    }

    @Test(timeout = 4000)
    public void testEqualToPredicateWithDifferentType() throws Throwable {
        // Given: An ALWAYS_FALSE ObjectPredicate
        Predicates.ObjectPredicate alwaysFalsePredicate = Predicates.ObjectPredicate.ALWAYS_FALSE;

        // When: Creating an equalTo predicate and testing with a different type
        Predicate<Predicates.ObjectPredicate> equalToPredicate = Predicates.equalTo(alwaysFalsePredicate);
        java.util.function.Predicate<Object> isEqualPredicate = java.util.function.Predicate.isEqual(equalToPredicate);
        CharMatcher charMatcher = CharMatcher.INVISIBLE;
        Predicate<CharMatcher> charMatcherPredicate = Predicates.equalTo(charMatcher);
        boolean result = isEqualPredicate.test(charMatcherPredicate);

        // Then: The result should be false
        assertFalse("Result should be false", result);
    }

    @Test(timeout = 4000)
    public void testEqualToPredicateWithSameType() throws Throwable {
        // Given: An ALWAYS_FALSE ObjectPredicate
        Predicates.ObjectPredicate alwaysFalsePredicate = Predicates.ObjectPredicate.ALWAYS_FALSE;

        // When: Creating an equalTo predicate and testing with the same type
        Predicate<Predicates.ObjectPredicate> equalToPredicate = Predicates.equalTo(alwaysFalsePredicate);
        java.util.function.Predicate<Predicates.ObjectPredicate> isEqualPredicate = java.util.function.Predicate.isEqual(equalToPredicate);
        boolean result = isEqualPredicate.test(alwaysFalsePredicate);

        // Then: The result should be false
        assertFalse("Result should be false", result);
    }

    @Test(timeout = 4000)
    public void testOrPredicateWithSamePredicate() throws Throwable {
        // Given: An ALWAYS_FALSE ObjectPredicate
        Predicates.ObjectPredicate alwaysFalsePredicate = Predicates.ObjectPredicate.ALWAYS_FALSE;

        // When: Creating an or predicate with the same predicate
        Predicate<CharMatcher> orPredicate = Predicates.or(alwaysFalsePredicate, alwaysFalsePredicate);
        java.util.function.Predicate<Predicates.ObjectPredicate> isEqualPredicate = java.util.function.Predicate.isEqual(orPredicate);
        boolean result = isEqualPredicate.test(alwaysFalsePredicate);

        // Then: The result should be false
        assertFalse("Result should be false", result);
    }

    @Test(timeout = 4000)
    public void testAndPredicateWithEmptyCollection() throws Throwable {
        // Given: An empty collection
        ArrayList<Predicates.ObjectPredicate> collection = new ArrayList<>();

        // When: Creating an and predicate and testing with ALWAYS_TRUE predicate
        Predicate<Predicate<CharMatcher>> andPredicate = Predicates.and(collection);
        java.util.function.Predicate<Predicates.ObjectPredicate> isEqualPredicate = java.util.function.Predicate.isEqual(andPredicate);
        Predicates.ObjectPredicate alwaysTruePredicate = Predicates.ObjectPredicate.ALWAYS_TRUE;
        boolean result = isEqualPredicate.test(alwaysTruePredicate);

        // Then: The result should be false
        assertFalse("Result should be false", result);
    }

    @Test(timeout = 4000)
    public void testNotPredicateWithOrPredicate() throws Throwable {
        // Given: A NOT_NULL ObjectPredicate
        Predicates.ObjectPredicate notNullPredicate = Predicates.ObjectPredicate.NOT_NULL;
        ArrayList<Predicates.ObjectPredicate> collection = new ArrayList<>();

        // When: Creating an or predicate and then a not predicate
        Predicate<Predicates.ObjectPredicate> orPredicate = Predicates.or(notNullPredicate, notNullPredicate);
        Predicate<Predicates.ObjectPredicate> notPredicate = Predicates.not(orPredicate);
        java.util.function.Predicate<Predicates.ObjectPredicate> isEqualPredicate = java.util.function.Predicate.isEqual(notPredicate);
        collection.add(notNullPredicate);
        boolean removed = collection.removeIf(isEqualPredicate);

        // Then: The collection should still contain the NOT_NULL predicate and nothing should be removed
        assertTrue("Collection should contain NOT_NULL predicate", collection.contains(notNullPredicate));
        assertFalse("Nothing should be removed", removed);
    }

    @Test(timeout = 4000)
    public void testNotPredicateWithAlwaysTrue() throws Throwable {
        // Given: An ALWAYS_TRUE ObjectPredicate
        Predicates.ObjectPredicate alwaysTruePredicate = Predicates.ObjectPredicate.ALWAYS_TRUE;

        // When: Creating a not predicate and using it with CharMatcher
        Predicate<Object> notPredicate = Predicates.not(alwaysTruePredicate);
        CharMatcher charMatcher = CharMatcher.forPredicate(notPredicate);
        char[] charArray = new char[10];
        CharBuffer charBuffer = CharBuffer.wrap(charArray);
        String result = charMatcher.trimAndCollapseFrom(charBuffer, '\u0000');

        // Then: The result should be a string of null characters
        assertEquals("Result should be a string of null characters", "\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000", result);
    }

    @Test(timeout = 4000)
    public void testApplyNotNullPredicate() throws Throwable {
        // Given: A NOT_NULL ObjectPredicate
        Predicates.ObjectPredicate notNullPredicate = Predicates.ObjectPredicate.NOT_NULL;

        // When: Applying the predicate to itself
        boolean result = notNullPredicate.apply(notNullPredicate);

        // Then: The result should be true
        assertTrue("Result should be true", result);
    }

    @Test(timeout = 4000)
    public void testApplyNotNullPredicateWithNull() throws Throwable {
        // Given: A NOT_NULL ObjectPredicate

        // When: Applying the predicate to null
        boolean result = Predicates.ObjectPredicate.NOT_NULL.apply(null);

        // Then: The result should be false
        assertFalse("Result should be false", result);
    }

    @Test(timeout = 4000)
    public void testApplyIsNullPredicateWithNull() throws Throwable {
        // Given: An IS_NULL ObjectPredicate

        // When: Applying the predicate to null
        boolean result = Predicates.ObjectPredicate.IS_NULL.apply(null);

        // Then: The result should be true
        assertTrue("Result should be true", result);
    }

    @Test(timeout = 4000)
    public void testCharMatcherWithIsNullPredicate() throws Throwable {
        // Given: An IS_NULL ObjectPredicate
        Predicates.ObjectPredicate isNullPredicate = Predicates.ObjectPredicate.IS_NULL;

        // When: Creating a CharMatcher for the predicate
        CharMatcher charMatcher = CharMatcher.forPredicate(isNullPredicate);
        char[] charArray = new char[8];
        CharBuffer charBuffer = CharBuffer.wrap(charArray);
        String result = charMatcher.trimAndCollapseFrom(charBuffer, 'b');

        // Then: The result should be a string of null characters
        assertEquals("Result should be a string of null characters", "\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000", result);
    }

    @Test(timeout = 4000)
    public void testCharMatcherWithAlwaysFalsePredicate() throws Throwable {
        // Given: An ALWAYS_FALSE ObjectPredicate
        Predicates.ObjectPredicate alwaysFalsePredicate = Predicates.ObjectPredicate.ALWAYS_FALSE;

        // When: Creating a CharMatcher for the predicate
        CharMatcher charMatcher = CharMatcher.forPredicate(alwaysFalsePredicate);

        // Then: The CharMatcher should not be null
        assertNotNull("CharMatcher should not be null", charMatcher);
    }

    @Test(timeout = 4000)
    public void testApplyAlwaysFalsePredicate() throws Throwable {
        // Given: An ALWAYS_FALSE ObjectPredicate
        Predicates.ObjectPredicate alwaysFalsePredicate = Predicates.ObjectPredicate.ALWAYS_FALSE;

        // When: Applying the predicate to itself
        boolean result = alwaysFalsePredicate.apply(alwaysFalsePredicate);

        // Then: The result should be false
        assertFalse("Result should be false", result);
    }

    @Test(timeout = 4000)
    public void testContainsPatternPredicateCreation() throws Throwable {
        // When: Creating a containsPattern predicate
        Predicate<CharSequence> predicate = Predicates.containsPattern("TNgJZkV0");

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testCharMatcherWithAlwaysTruePredicate() throws Throwable {
        // Given: An ALWAYS_TRUE ObjectPredicate
        Predicates.ObjectPredicate alwaysTruePredicate = Predicates.ObjectPredicate.ALWAYS_TRUE;

        // When: Creating a CharMatcher for the predicate
        CharMatcher charMatcher = CharMatcher.forPredicate(alwaysTruePredicate);
        char[] charArray = new char[10];
        CharBuffer charBuffer = CharBuffer.wrap(charArray);
        String result = charMatcher.trimAndCollapseFrom(charBuffer, '\u0000');

        // Then: The result should be an empty string
        assertEquals("Result should be an empty string", "", result);
    }

    @Test(timeout = 4000)
    public void testInPredicateWithEmptyPriorityQueue() throws Throwable {
        // Given: An empty PriorityQueue
        PriorityQueue<CharMatcher> priorityQueue = new PriorityQueue<>();

        // When: Creating an in predicate and using it with CharMatcher
        Predicate<Object> inPredicate = Predicates.in(priorityQueue);
        CharMatcher charMatcher = CharMatcher.forPredicate(inPredicate);

        // Then: The priority queue should not contain the CharMatcher
        assertFalse("PriorityQueue should not contain CharMatcher", priorityQueue.contains(charMatcher));
    }

    @Test(timeout = 4000)
    public void testDefensiveCopyWithEmptyHashSet() throws Throwable {
        // Given: An empty HashSet
        HashSet<CharMatcher> hashSet = new HashSet<>(13);

        // When: Creating a defensive copy and an in predicate
        List<CharMatcher> list = Predicates.defensiveCopy(hashSet);
        Predicate<CharMatcher> inPredicate = Predicates.in(list);
        HashSet<Predicate<CharMatcher>> predicateHashSet = new HashSet<>();
        boolean added = predicateHashSet.add(inPredicate);

        // Then: The predicate should be added to the HashSet
        assertTrue("Predicate should be added to HashSet", added);
    }

    @Test(timeout = 4000)
    public void testComposePredicateWithIdentityConverter() throws Throwable {
        // Given: A NOT_NULL ObjectPredicate
        Predicates.ObjectPredicate notNullPredicate = Predicates.ObjectPredicate.NOT_NULL;

        // When: Creating an or predicate and composing it with an identity converter
        Predicate<Predicates.ObjectPredicate> orPredicate = Predicates.or(notNullPredicate, notNullPredicate);
        Converter<Predicates.ObjectPredicate, Predicates.ObjectPredicate> identityConverter = Converter.identity();
        Predicate<Predicates.ObjectPredicate> composedPredicate = Predicates.compose(orPredicate, identityConverter);

        // Then: The composed predicate should not be equal to the original or predicate
        assertFalse("Composed predicate should not be equal to original or predicate", composedPredicate.equals(orPredicate));
    }

    @Test(timeout = 4000)
    public void testContainsPatternPredicateWithPattern() throws Throwable {
        // Given: A compiled pattern
        Pattern pattern = Pattern.compile("", (-1238));

        // When: Creating a contains predicate
        Predicate<CharSequence> predicate = Predicates.contains(pattern);

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testComposePredicateWithEmptyCollection() throws Throwable {
        // Given: An empty collection
        ArrayList<Predicates.ObjectPredicate> collection = new ArrayList<>();

        // When: Creating an in predicate and composing it with an identity converter
        Predicate<Predicates.ObjectPredicate> inPredicate = Predicates.in(collection);
        Converter<Predicates.ObjectPredicate, Predicates.ObjectPredicate> identityConverter = Converter.identity();
        Predicate<Predicates.ObjectPredicate> composedPredicate = Predicates.compose(inPredicate, identityConverter);
        java.util.function.Predicate<Predicates.ObjectPredicate> isEqualPredicate = java.util.function.Predicate.isEqual(composedPredicate);
        Predicates.ObjectPredicate alwaysFalsePredicate = Predicates.ObjectPredicate.ALWAYS_FALSE;
        boolean result = isEqualPredicate.test(alwaysFalsePredicate);

        // Then: The result should be false
        assertFalse("Result should be false", result);
    }

    @Test(timeout = 4000)
    public void testNotNullPredicateCreationForCharMatcher() throws Throwable {
        // When: Creating a notNull predicate for CharMatcher
        Predicate<CharMatcher> predicate = Predicates.notNull();

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testOrPredicateWithEmptyCollection() throws Throwable {
        // Given: An empty collection
        ArrayList<Predicates.ObjectPredicate> collection = new ArrayList<>();

        // When: Creating an or predicate and using it with CharMatcher
        Predicate<Object> orPredicate = Predicates.or(collection);
        CharMatcher charMatcher = CharMatcher.forPredicate(orPredicate);

        // Then: The CharMatcher should not be null
        assertNotNull("CharMatcher should not be null", charMatcher);
    }

    @Test(timeout = 4000)
    public void testEqualToPredicateWithNull() throws Throwable {
        // When: Creating an equalTo predicate with null
        Predicate<CharMatcher> predicate = Predicates.equalTo(null);

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testOrPredicateWithNullArray() throws Throwable {
        // Given: An array of predicates with null elements
        Predicate<Class<CharMatcher>>[] predicateArray = (Predicate<Class<CharMatcher>>[]) Array.newInstance(Predicate.class, 1);

        // When: Creating an or predicate with the array
        // Then: Expecting a NullPointerException
        try {
            Predicates.or(predicateArray);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            // Expected exception
        }
    }

    @Test(timeout = 4000)
    public void testAndPredicateWithObjectPredicateArray() throws Throwable {
        // Given: An array of ObjectPredicates
        Predicates.ObjectPredicate[] objectPredicateArray = Predicates.ObjectPredicate.values();

        // When: Creating an and predicate with the array
        Predicate<Predicate<CharMatcher>> predicate = Predicates.and(objectPredicateArray);

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testCharMatcherWithNotPredicate() throws Throwable {
        // Given: An IS_NULL ObjectPredicate
        Predicates.ObjectPredicate isNullPredicate = Predicates.ObjectPredicate.IS_NULL;

        // When: Creating a not predicate and using it with CharMatcher
        Predicate<Object> notPredicate = Predicates.not(isNullPredicate);
        CharMatcher charMatcher = CharMatcher.forPredicate(notPredicate);
        char[] charArray = new char[8];
        CharBuffer charBuffer = CharBuffer.wrap(charArray);
        String result = charMatcher.trimAndCollapseFrom(charBuffer, 'b');

        // Then: The result should be an empty string
        assertEquals("Result should be an empty string", "", result);
    }

    @Test(timeout = 4000)
    public void testAssignableFromPredicateCreation() throws Throwable {
        // Given: A class type
        Class<Predicates.ObjectPredicate> objectPredicateClass = Predicates.ObjectPredicate.class;

        // When: Creating an assignableFrom predicate
        Predicate<Class<?>> predicate = Predicates.assignableFrom(objectPredicateClass);

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testAlwaysFalsePredicateCreation() throws Throwable {
        // When: Creating an alwaysFalse predicate
        Predicate<CharMatcher> predicate = Predicates.alwaysFalse();

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testAlwaysTruePredicateCreation() throws Throwable {
        // When: Creating an alwaysTrue predicate
        Predicate<Predicates.ObjectPredicate> predicate = Predicates.alwaysTrue();

        // Then: The predicate should not be null
        assertNotNull("Predicate should not be null", predicate);
    }

    @Test(timeout = 4000)
    public void testEqualToPredicateWithCharMatcher() throws Throwable {
        // Given: A CharMatcher
        CharMatcher charMatcher = CharMatcher.ASCII;

        // When: Creating an equalTo predicate
        Predicate<CharMatcher> predicate = Predicates.equalTo(charMatcher);
        HashSet<Predicate<CharMatcher>> predicateHashSet = new HashSet<>();
        boolean added = predicateHashSet.add(predicate);

        // Then: The predicate should be added to the HashSet
        assertTrue("Predicate should be added to HashSet", added);
    }

    @Test(timeout = 4000)
    public void testInstanceOfPredicateWithObjectPredicateClass() throws Throwable {
        // Given: A class type
        Class<Predicates.ObjectPredicate> objectPredicateClass = Predicates.ObjectPredicate.class;

        // When: Creating an instanceOf predicate and using it with CharMatcher
        Predicate<Object> instanceOfPredicate = Predicates.instanceOf(objectPredicateClass);
        CharMatcher charMatcher = CharMatcher.forPredicate(instanceOfPredicate);

        // Then: The CharMatcher should not be null
        assertNotNull("CharMatcher should not be null", charMatcher);
    }

    @Test(timeout = 4000)
    public void testCharMatcherWithNotNullPredicate() throws Throwable {
        // Given: A NOT_NULL ObjectPredicate
        Predicates.ObjectPredicate notNullPredicate = Predicates.ObjectPredicate.NOT_NULL;

        // When: Creating a CharMatcher for the predicate
        CharMatcher charMatcher = CharMatcher.forPredicate(notNullPredicate);

        // Then: The CharMatcher should not be null
        assertNotNull("CharMatcher should not be null", charMatcher);
    }

    @Test(timeout = 4000)
    public void testCharMatcherWithAndPredicate() throws Throwable {
        // Given: An empty collection
        ArrayList<Predicates.ObjectPredicate> collection = new ArrayList<>();

        // When: Creating an and predicate and using it with CharMatcher
        Predicate<Predicate<CharMatcher>> andPredicate = Predicates.and(collection);
        Predicate<Object> equalToPredicate = Predicates.equalTo(andPredicate);
        CharMatcher charMatcher = CharMatcher.forPredicate(equalToPredicate);

        // Then: The CharMatcher should not be null
        assertNotNull("CharMatcher should not be null", charMatcher);
    }

    @Test(timeout = 4000)
    public void testAndPredicateWithInstanceOfPredicate() throws Throwable {
        // Given: A class type
        Class<CharMatcher> charMatcherClass = CharMatcher.class;

        // When: Creating an instanceOf predicate and an and predicate
        Predicate<Object> instanceOfPredicate = Predicates.instanceOf(charMatcherClass);
        LinkedHashSet<CharMatcher> linkedHashSet = new LinkedHashSet<>();
        Predicate<Class<CharMatcher>> andPredicate = Predicates.and(instanceOfPredicate, instanceOfPredicate);
        boolean removed = linkedHashSet.remove(andPredicate);

        // Then: Nothing should be removed from the LinkedHashSet
        assertFalse("Nothing should be removed from LinkedHashSet", removed);
    }