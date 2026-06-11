private static final int TIMEOUT = 4000;
    private static final int EMPTY_ARRAY_SIZE = 0;
    private static final int SINGLE_ELEMENT_ARRAY_SIZE = 1;
    private static final int MULTI_ELEMENT_ARRAY_SIZE = 8;

    @Test(timeout = TIMEOUT)
    public void testIteratorNotNull() throws Throwable {
        // Given: A Fold with a DefaultDataset and an array of indices
        DefaultDataset dataset = new DefaultDataset();
        int[] indices = new int[MULTI_ELEMENT_ARRAY_SIZE];
        Fold fold = new Fold(dataset, indices);

        // When: Retrieving the iterator
        Iterator<Instance> iterator = fold.iterator();

        // Then: The iterator should not be null
        assertNotNull("Iterator should not be null", iterator);
    }

    @Test(timeout = TIMEOUT)
    public void testInstanceAccessThrowsException() throws Throwable {
        // Given: A Fold with a DefaultDataset and an array of indices
        DefaultDataset dataset = new DefaultDataset();
        int[] indices = new int[5];
        Fold fold = new Fold(dataset, indices);

        // When: Accessing an instance at an invalid index
        // Then: Expect an ArrayIndexOutOfBoundsException
        try {
            fold.instance(0);
            fail("Expecting exception: ArrayIndexOutOfBoundsException");
        } catch (ArrayIndexOutOfBoundsException e) {
            verifyException("java.util.Vector", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testCopyFold() throws Throwable {
        // Given: A Fold with a DefaultDataset containing a DenseInstance
        DefaultDataset dataset = new DefaultDataset();
        double[] values = new double[5];
        DenseInstance instance = new DenseInstance(values);
        dataset.add(instance);
        int[] indices = new int[SINGLE_ELEMENT_ARRAY_SIZE];
        Fold fold = new Fold(dataset, indices);

        // When: Copying the fold
        Dataset copiedDataset = fold.copy();

        // Then: The copied dataset should have the same size as the fold
        assertEquals("Copied dataset size should match fold size", SINGLE_ELEMENT_ARRAY_SIZE, copiedDataset.size());
    }

    @Test(timeout = TIMEOUT)
    public void testToArrayWithPredefinedArray() throws Throwable {
        // Given: A Fold with a DefaultDataset containing a SparseInstance
        DefaultDataset dataset = new DefaultDataset();
        double[] values = new double[1];
        SparseInstance instance = new SparseInstance(values, 1847.67361);
        dataset.add(instance);
        int[] indices = new int[SINGLE_ELEMENT_ARRAY_SIZE];
        Fold fold = new Fold(dataset, indices);
        Object[] predefinedArray = new Object[6];

        // When: Converting the fold to an array using a predefined array
        Object[] resultArray = fold.toArray(predefinedArray);

        // Then: The result array should be the same as the predefined array
        assertSame("Result array should be the same as predefined array", predefinedArray, resultArray);
    }

    @Test(timeout = TIMEOUT)
    public void testToArrayThrowsNullPointerException() throws Throwable {
        // Given: A Fold with a null Dataset
        int[] indices = new int[2];
        Fold fold = new Fold(null, indices);

        // When: Converting the fold to an array
        // Then: Expect a NullPointerException
        try {
            fold.toArray();
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testToArrayWithEmptyFold() throws Throwable {
        // Given: A Fold with an empty DefaultDataset
        DefaultDataset dataset = new DefaultDataset();
        int[] indices = new int[EMPTY_ARRAY_SIZE];
        Fold fold = new Fold(dataset, indices);

        // When: Converting the fold to an array
        Object[] resultArray = fold.toArray();

        // Then: The result array should be empty
        assertEquals("Result array should be empty", EMPTY_ARRAY_SIZE, resultArray.length);
    }

    @Test(timeout = TIMEOUT)
    public void testFoldIteratorHasPrevious() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Creating a FoldIterator with a starting index
        Fold.FoldIterator iterator = fold.new FoldIterator(1);

        // Then: The iterator should have a previous element
        assertTrue("Iterator should have previous element", iterator.hasPrevious());
        assertEquals("Next index should be 1", 1, iterator.nextIndex());
    }

    @Test(timeout = TIMEOUT)
    public void testFoldIteratorNoPrevious() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Creating a FoldIterator without a starting index
        Fold.FoldIterator iterator = fold.new FoldIterator();

        // Then: The iterator should not have a previous element
        assertFalse("Iterator should not have previous element", iterator.hasPrevious());
        assertEquals("Next index should be 0", 0, iterator.nextIndex());
    }

    @Test(timeout = TIMEOUT)
    public void testListIteratorNoPrevious() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Creating a ListIterator
        ListIterator<Instance> listIterator = fold.listIterator();

        // Then: The list iterator should not have a previous element
        assertFalse("ListIterator should not have previous element", listIterator.hasPrevious());
    }

    @Test(timeout = TIMEOUT)
    public void testRemoveThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Attempting to remove an element
        // Then: Expect an UnsupportedOperationException
        try {
            fold.remove(1396);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testRemoveObjectThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        int[] indices = new int[SINGLE_ELEMENT_ARRAY_SIZE];
        Fold fold = new Fold(null, indices);

        // When: Attempting to remove an object
        // Then: Expect an UnsupportedOperationException
        try {
            fold.remove((Object) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testContainsThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Checking if the fold contains an object
        // Then: Expect an UnsupportedOperationException
        try {
            fold.contains((Object) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testSetThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Attempting to set an element
        // Then: Expect an UnsupportedOperationException
        try {
            fold.set(1, (Instance) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testContainsAllThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Checking if the fold contains all elements of a collection
        // Then: Expect an UnsupportedOperationException
        try {
            fold.containsAll((Collection<?>) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testRemoveAllThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Attempting to remove all elements of a collection
        // Then: Expect an UnsupportedOperationException
        try {
            fold.removeAll((Collection<?>) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testAddThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);
        SparseInstance instance = new SparseInstance();

        // When: Attempting to add an instance
        // Then: Expect an UnsupportedOperationException
        try {
            fold.add(instance);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testClearThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with a DefaultDataset and indices
        DefaultDataset dataset = new DefaultDataset();
        int[] indices = new int[SINGLE_ELEMENT_ARRAY_SIZE];
        Fold fold = new Fold(dataset, indices);

        // When: Attempting to clear the fold
        // Then: Expect an UnsupportedOperationException
        try {
            fold.clear();
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testNoAttributes() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Retrieving the number of attributes
        int numAttributes = fold.noAttributes();

        // Then: The number of attributes should be zero
        assertEquals("Number of attributes should be zero", 0, numAttributes);
    }

    @Test(timeout = TIMEOUT)
    public void testGetThrowsNullPointerException() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Attempting to get an element at an index
        // Then: Expect a NullPointerException
        try {
            fold.get(522);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testKNearestThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with an empty DefaultDataset
        DefaultDataset dataset = new DefaultDataset();
        int[] indices = new int[EMPTY_ARRAY_SIZE];
        Fold fold = new Fold(dataset, indices);
        DenseInstance instance = new DenseInstance(EMPTY_ARRAY_SIZE);
        SpearmanFootruleDistance distance = new SpearmanFootruleDistance();

        // When: Attempting to find k-nearest neighbors
        // Then: Expect an UnsupportedOperationException
        try {
            fold.kNearest(0, instance, distance);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testLastIndexOfThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        int[] indices = new int[EMPTY_ARRAY_SIZE];
        Fold fold = new Fold(null, indices);

        // When: Attempting to find the last index of an object
        // Then: Expect an UnsupportedOperationException
        try {
            fold.lastIndexOf((Object) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testFoldSize() throws Throwable {
        // Given: A Fold with a DefaultDataset and indices
        DefaultDataset dataset = new DefaultDataset();
        int[] indices = new int[SINGLE_ELEMENT_ARRAY_SIZE];
        Fold fold = new Fold(dataset, indices);

        // When: Retrieving the size of the fold
        int size = fold.size();

        // Then: The size should match the number of indices
        assertEquals("Fold size should match number of indices", SINGLE_ELEMENT_ARRAY_SIZE, size);
    }

    @Test(timeout = TIMEOUT)
    public void testClassValueReturnsNull() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Retrieving the class value at an index
        Object classValue = fold.classValue(-1413);

        // Then: The class value should be null
        assertNull("Class value should be null", classValue);
    }

    @Test(timeout = TIMEOUT)
    public void testListIteratorWithIndexHasPrevious() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Creating a ListIterator with a starting index
        ListIterator<Instance> listIterator = fold.listIterator(5);

        // Then: The list iterator should have a previous element
        assertTrue("ListIterator should have previous element", listIterator.hasPrevious());
    }

    @Test(timeout = TIMEOUT)
    public void testIndexOfThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Attempting to find the index of an object
        // Then: Expect an UnsupportedOperationException
        try {
            fold.indexOf(dataset);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testAddAllWithIndexThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Attempting to add all elements of a collection at an index
        // Then: Expect an UnsupportedOperationException
        try {
            fold.addAll(-1, (Collection<? extends Instance>) dataset);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testAddAllThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Attempting to add all elements of a collection
        // Then: Expect an UnsupportedOperationException
        try {
            fold.addAll((Collection<? extends Instance>) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testFoldsThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);
        MockRandom random = new MockRandom();

        // When: Attempting to create folds
        // Then: Expect an UnsupportedOperationException
        try {
            fold.folds(-1049, random);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testSubListThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with a DefaultDataset and indices
        DefaultDataset dataset = new DefaultDataset();
        int[] indices = new int[SINGLE_ELEMENT_ARRAY_SIZE];
        Fold fold = new Fold(dataset, indices);

        // When: Attempting to create a sublist
        // Then: Expect an UnsupportedOperationException
        try {
            fold.subList(0, 0);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testClassIndexThrowsNullPointerException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        int[] indices = new int[2];
        Fold fold = new Fold(null, indices);

        // When: Attempting to find the class index of an object
        // Then: Expect a NullPointerException
        try {
            fold.classIndex((Object) null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testClassesReturnsEmptySet() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Retrieving the classes
        SortedSet<Object> classes = fold.classes();

        // Then: The classes set should be empty
        assertEquals("Classes set should be empty", 0, classes.size());
    }

    @Test(timeout = TIMEOUT)
    public void testRetainAllThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Attempting to retain all elements of a collection
        // Then: Expect an UnsupportedOperationException
        try {
            fold.retainAll((Collection<?>) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testAddWithIndexThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with null Dataset and indices
        int[] indices = new int[EMPTY_ARRAY_SIZE];
        Fold fold = new Fold(null, indices);
        SparseInstance instance = new SparseInstance();

        // When: Attempting to add an instance at an index
        // Then: Expect an UnsupportedOperationException
        try {
            fold.add(1032, instance);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testIsEmptyReturnsFalse() throws Throwable {
        // Given: A Fold with null Dataset and indices
        Fold fold = new Fold(null, null);

        // When: Checking if the fold is empty
        boolean isEmpty = fold.isEmpty();

        // Then: The fold should not be empty
        assertFalse("Fold should not be empty", isEmpty);
    }

    @Test(timeout = TIMEOUT)
    public void testFoldIteratorPreviousIndex() throws Throwable {
        // Given: A Fold with a DefaultDataset and indices
        DefaultDataset dataset = new DefaultDataset();
        int[] indices = new int[3];
        Fold fold = new Fold(dataset, indices);

        // When: Creating a FoldIterator
        Fold.FoldIterator iterator = fold.new FoldIterator();

        // Then: The previous index should be zero
        assertEquals("Previous index should be zero", 0, iterator.previousIndex());
    }

    @Test(timeout = TIMEOUT)
    public void testFoldIteratorAddThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Creating a FoldIterator with a starting index
        Fold.FoldIterator iterator = fold.new FoldIterator(6);

        // Then: Attempting to add an instance should throw an UnsupportedOperationException
        try {
            iterator.add((Instance) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold$FoldIterator", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testFoldIteratorPreviousThrowsNullPointerException() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Creating a FoldIterator
        Fold.FoldIterator iterator = fold.new FoldIterator();

        // Then: Attempting to retrieve the previous element should throw a NullPointerException
        try {
            iterator.previous();
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("net.sf.javaml.core.Fold", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testFoldIteratorNextIndex() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Creating a FoldIterator
        Fold.FoldIterator iterator = fold.new FoldIterator();

        // Then: The next index should be zero
        assertEquals("Next index should be zero", 0, iterator.nextIndex());
    }

    @Test(timeout = TIMEOUT)
    public void testFoldIteratorRemoveThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Creating a FoldIterator
        Fold.FoldIterator iterator = fold.new FoldIterator();

        // Then: Attempting to remove an element should throw an UnsupportedOperationException
        try {
            iterator.remove();
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold$FoldIterator", e);
        }
    }

    @Test(timeout = TIMEOUT)
    public void testFoldIteratorSetThrowsUnsupportedOperationException() throws Throwable {
        // Given: A Fold with a DefaultDataset and null indices
        DefaultDataset dataset = new DefaultDataset();
        Fold fold = new Fold(dataset, null);

        // When: Creating a FoldIterator
        Fold.FoldIterator iterator = fold.new FoldIterator();

        // Then: Attempting to set an element should throw an UnsupportedOperationException
        try {
            iterator.set((Instance) null);
            fail("Expecting exception: UnsupportedOperationException");
        } catch (UnsupportedOperationException e) {
            verifyException("net.sf.javaml.core.Fold$FoldIterator", e);
        }
    }