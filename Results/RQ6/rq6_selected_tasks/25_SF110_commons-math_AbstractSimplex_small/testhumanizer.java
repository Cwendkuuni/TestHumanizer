private static final double TOLERANCE = 0.01;
    private static final double TEST_VALUE = 2229.24;
    private static final double[] SINGLE_DIMENSION_ARRAY = {1.0};
    private static final double[] MULTI_DIMENSION_ARRAY = {2509.0325528834, 2229.24, 2229.24, 2229.24};

    @Test(timeout = 4000)
    public void testIterateWithNullFunctionAndComparator() {
        // Given
        NelderMeadSimplex nelderMeadSimplex = new NelderMeadSimplex(2, 2);

        // When & Then
        try {
            nelderMeadSimplex.iterate(null, null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testGetSizeWithUninitializedSimplex() {
        // Given
        NelderMeadSimplex nelderMeadSimplex = new NelderMeadSimplex(115, 861.555043104, 861.555043104, -1996.384, 115);

        // When & Then
        try {
            nelderMeadSimplex.getSize();
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testGetPointsWithUninitializedSimplex() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(SINGLE_DIMENSION_ARRAY);

        // When & Then
        try {
            multiDirectionalSimplex.getPoints();
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testGetDimension() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(SINGLE_DIMENSION_ARRAY);

        // When
        int dimension = multiDirectionalSimplex.getDimension();

        // Then
        assertEquals("Dimension should be 1", 1, dimension);
    }

    @Test(timeout = 4000)
    public void testSetPointsWithMismatchedDimensions() {
        // Given
        double[][] initialConfiguration = new double[1][8];
        double[] startPoint = new double[0];
        initialConfiguration[0] = startPoint;
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(initialConfiguration, 2, 54.93052);
        multiDirectionalSimplex.build(startPoint);
        PointValuePair[] pointValuePairArray = new PointValuePair[3];

        // When & Then
        try {
            multiDirectionalSimplex.setPoints(pointValuePairArray);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testSetPointsWithMatchingDimensions() {
        // Given
        double[][] initialConfiguration = new double[1][8];
        double[] startPoint = new double[0];
        initialConfiguration[0] = startPoint;
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(initialConfiguration, 26, 54.93052);
        multiDirectionalSimplex.build(startPoint);
        PointValuePair[] pointValuePairArray = new PointValuePair[1];

        // When
        multiDirectionalSimplex.setPoints(pointValuePairArray);

        // Then
        assertEquals("Size should be 1", 1, multiDirectionalSimplex.getSize());
    }

    @Test(timeout = 4000)
    public void testSetPointWithOutOfRangeIndex() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(SINGLE_DIMENSION_ARRAY);
        multiDirectionalSimplex.build(SINGLE_DIMENSION_ARRAY);

        // When & Then
        try {
            multiDirectionalSimplex.setPoint(117, null);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testGetPoint() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(MULTI_DIMENSION_ARRAY);
        multiDirectionalSimplex.build(MULTI_DIMENSION_ARRAY);

        // When
        PointValuePair pointValuePair = multiDirectionalSimplex.getPoint(2);

        // Then
        assertArrayEquals("Array should match", MULTI_DIMENSION_ARRAY, MULTI_DIMENSION_ARRAY, TOLERANCE);
        assertNotNull("PointValuePair should not be null", pointValuePair);
    }

    @Test(timeout = 4000)
    public void testGetPointWithNegativeIndex() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(87, 87);

        // When & Then
        try {
            multiDirectionalSimplex.getPoint(-3379);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testReplaceWorstPoint() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(SINGLE_DIMENSION_ARRAY);
        Comparator<PointValuePair> comparator = mock(Comparator.class, new ViolatedAssumptionAnswer());
        doReturn(123).when(comparator).compare(any(PointValuePair.class), any(PointValuePair.class));
        multiDirectionalSimplex.build(SINGLE_DIMENSION_ARRAY);
        PointValuePair pointValuePair = new PointValuePair(SINGLE_DIMENSION_ARRAY, -487.555, false);

        // When
        multiDirectionalSimplex.replaceWorstPoint(pointValuePair, comparator);

        // Then
        assertEquals("Size should be 2", 2, multiDirectionalSimplex.getSize());
    }

    @Test(timeout = 4000)
    public void testReplaceWorstPointWithEqualComparator() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(SINGLE_DIMENSION_ARRAY);
        Comparator<PointValuePair> comparator = mock(Comparator.class, new ViolatedAssumptionAnswer());
        doReturn(0).when(comparator).compare(any(PointValuePair.class), any(PointValuePair.class));
        multiDirectionalSimplex.build(SINGLE_DIMENSION_ARRAY);
        PointValuePair pointValuePair = new PointValuePair(SINGLE_DIMENSION_ARRAY, TEST_VALUE);

        // When
        multiDirectionalSimplex.replaceWorstPoint(pointValuePair, comparator);

        // Then
        assertEquals("Dimension should be 1", 1, multiDirectionalSimplex.getDimension());
    }

    @Test(timeout = 4000)
    public void testEvaluateWithNullFunctionAndComparator() {
        // Given
        double[][] initialConfiguration = new double[1][8];
        double[] startPoint = new double[0];
        initialConfiguration[0] = startPoint;
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(initialConfiguration, 26, 54.93052);
        multiDirectionalSimplex.build(startPoint);
        PointValuePair pointValuePair = new PointValuePair(startPoint, 26);

        // When
        multiDirectionalSimplex.replaceWorstPoint(pointValuePair, null);
        multiDirectionalSimplex.evaluate(null, null);

        // Then
        assertEquals("Size should be 1", 1, multiDirectionalSimplex.getSize());
    }

    @Test(timeout = 4000)
    public void testGetPointWithOutOfRangeIndex() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(SINGLE_DIMENSION_ARRAY);
        multiDirectionalSimplex.build(SINGLE_DIMENSION_ARRAY);

        // When & Then
        try {
            multiDirectionalSimplex.getPoint(458);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testBuildWithMismatchedDimensions() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(87, 87);
        double[] startPoint = new double[0];

        // When & Then
        try {
            multiDirectionalSimplex.build(startPoint);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testConstructorWithMismatchedDimensions() {
        // Given
        double[][] initialConfiguration = new double[3][7];
        double[] firstPoint = {4144, 0};
        initialConfiguration[0] = firstPoint;
        double[] secondPoint = new double[2];
        initialConfiguration[1] = secondPoint;

        // When & Then
        try {
            new MultiDirectionalSimplex(initialConfiguration, 3629.82717201, -4739.939834052583);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testConstructorWithEqualVertices() {
        // Given
        double[][] initialConfiguration = new double[3][7];
        double[] point = new double[2];
        initialConfiguration[0] = point;
        initialConfiguration[1] = point;

        // When & Then
        try {
            new MultiDirectionalSimplex(initialConfiguration, 3629.82717201, -4739.939834052583);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testConstructorWithEmptyConfiguration() {
        // Given
        double[][] initialConfiguration = new double[0][0];

        // When & Then
        try {
            new NelderMeadSimplex(initialConfiguration);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testConstructorWithSingleDimensionArray() {
        // Given
        double[] singleDimensionArray = new double[1];

        // When & Then
        try {
            new MultiDirectionalSimplex(singleDimensionArray);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testConstructorWithEmptyArray() {
        // Given
        double[] emptyArray = new double[0];

        // When & Then
        try {
            new MultiDirectionalSimplex(emptyArray);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testConstructorWithNullArray() {
        // Given
        double[] nullArray = null;

        // When & Then
        try {
            new MultiDirectionalSimplex(nullArray, -1.0, -1.0);
            fail("Expecting exception: IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testIterateWithNullFunctionAndComparatorAfterBuild() {
        // Given
        double[][] initialConfiguration = new double[1][8];
        double[] startPoint = new double[0];
        initialConfiguration[0] = startPoint;
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(initialConfiguration, 26, 54.93052);
        multiDirectionalSimplex.build(startPoint);

        // When & Then
        try {
            multiDirectionalSimplex.iterate(null, null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }

    @Test(timeout = 4000)
    public void testSetPointWithNegativeIndex() {
        // Given
        MultiDirectionalSimplex multiDirectionalSimplex = new MultiDirectionalSimplex(34, 34);

        // When & Then
        try {
            multiDirectionalSimplex.setPoint(-4617, null);
            fail("Expecting exception: NullPointerException");
        } catch (NullPointerException e) {
            verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
        }
    }