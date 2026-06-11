@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      NelderMeadSimplex nelderMeadSimplex0 = new NelderMeadSimplex(37);
      // Undeclared exception!
      try { 
        nelderMeadSimplex0.iterate((MultivariateFunction) null, (Comparator<PointValuePair>) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.getSize();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      double[][] doubleArray0 = new double[2][1];
      double[] doubleArray1 = new double[1];
      doubleArray1[0] = 2177.617162555;
      doubleArray0[0] = doubleArray1;
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(doubleArray0);
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.getPoints();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      double[] doubleArray0 = new double[1];
      doubleArray0[0] = 674.149;
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(doubleArray0, 674.149, (-1182));
      int int0 = multiDirectionalSimplex0.getDimension();
      assertEquals(1, int0);
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      double[] doubleArray0 = new double[1];
      multiDirectionalSimplex0.build(doubleArray0);
      PointValuePair[] pointValuePairArray0 = new PointValuePair[0];
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.setPoints(pointValuePairArray0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 0 != 2
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      double[] doubleArray0 = new double[1];
      multiDirectionalSimplex0.build(doubleArray0);
      PointValuePair pointValuePair0 = new PointValuePair(doubleArray0, 1, true);
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.setPoint(1493, pointValuePair0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 1,493 out of [0, 1] range
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(46, (-1859), (-1859), 46);
      double[] doubleArray0 = new double[2];
      PointValuePair pointValuePair0 = new PointValuePair(doubleArray0, (-1859), true);
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.setPoint((-1859), pointValuePair0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      double[] doubleArray0 = new double[1];
      multiDirectionalSimplex0.build(doubleArray0);
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.getPoint(1778);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 1,778 out of [0, 1] range
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      double[] doubleArray0 = new double[1];
      multiDirectionalSimplex0.build(doubleArray0);
      PointValuePair pointValuePair0 = multiDirectionalSimplex0.getPoint(1);
      Comparator<PointValuePair> comparator0 = (Comparator<PointValuePair>) mock(Comparator.class, new ViolatedAssumptionAnswer());
      doReturn(0).when(comparator0).compare(any(org.apache.commons.math3.optim.PointValuePair.class) , any(org.apache.commons.math3.optim.PointValuePair.class));
      multiDirectionalSimplex0.replaceWorstPoint(pointValuePair0, comparator0);
      assertEquals(1, multiDirectionalSimplex0.getDimension());
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      double[] doubleArray0 = new double[1];
      multiDirectionalSimplex0.build(doubleArray0);
      PointValuePair pointValuePair0 = multiDirectionalSimplex0.getPoint(1);
      Comparator<PointValuePair> comparator0 = (Comparator<PointValuePair>) mock(Comparator.class, new ViolatedAssumptionAnswer());
      doReturn(1).when(comparator0).compare(any(org.apache.commons.math3.optim.PointValuePair.class) , any(org.apache.commons.math3.optim.PointValuePair.class));
      multiDirectionalSimplex0.replaceWorstPoint(pointValuePair0, comparator0);
      assertEquals(1, multiDirectionalSimplex0.getDimension());
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      double[] doubleArray0 = new double[1];
      multiDirectionalSimplex0.build(doubleArray0);
      PointValuePair[] pointValuePairArray0 = new PointValuePair[2];
      PointValuePair pointValuePair0 = new PointValuePair(doubleArray0, 1.0);
      pointValuePairArray0[0] = pointValuePair0;
      multiDirectionalSimplex0.setPoints(pointValuePairArray0);
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.evaluate((MultivariateFunction) null, (Comparator<PointValuePair>) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      assertEquals(1, multiDirectionalSimplex0.getDimension());
      
      double[] doubleArray0 = new double[1];
      multiDirectionalSimplex0.build(doubleArray0);
      assertEquals(2, multiDirectionalSimplex0.getSize());
      
      double[][] doubleArray1 = new double[1][7];
      doubleArray1[0] = doubleArray0;
      Well44497a well44497a0 = new Well44497a(1);
      UnitSphereRandomVectorGenerator unitSphereRandomVectorGenerator0 = new UnitSphereRandomVectorGenerator(1, well44497a0);
      MicrosphereInterpolatingFunction microsphereInterpolatingFunction0 = new MicrosphereInterpolatingFunction(doubleArray1, doubleArray0, 1, 1, unitSphereRandomVectorGenerator0);
      Comparator<PointValuePair> comparator0 = (Comparator<PointValuePair>) mock(Comparator.class, new ViolatedAssumptionAnswer());
      doReturn(0).when(comparator0).compare(any(org.apache.commons.math3.optim.PointValuePair.class) , any(org.apache.commons.math3.optim.PointValuePair.class));
      multiDirectionalSimplex0.evaluate(microsphereInterpolatingFunction0, comparator0);
      assertArrayEquals(new double[] {0.0}, doubleArray0, 0.01);
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      double[] doubleArray0 = new double[19];
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.build(doubleArray0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 1 != 19
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      double[] doubleArray0 = new double[1];
      double[][] doubleArray1 = new double[2][9];
      doubleArray1[0] = doubleArray0;
      doubleArray1[1] = doubleArray0;
      MultiDirectionalSimplex multiDirectionalSimplex0 = null;
      try {
        multiDirectionalSimplex0 = new MultiDirectionalSimplex(doubleArray1, 1, 1.0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // equal vertices 1 and 0 in simplex configuration
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      double[][] doubleArray0 = new double[1][7];
      double[] doubleArray1 = new double[0];
      doubleArray0[0] = doubleArray1;
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(doubleArray0);
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.getPoint((-784));
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      double[][] doubleArray0 = new double[0][5];
      MultiDirectionalSimplex multiDirectionalSimplex0 = null;
      try {
        multiDirectionalSimplex0 = new MultiDirectionalSimplex(doubleArray0, 555.0573578, 555.0573578);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // simplex must contain at least one point
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      double[][] doubleArray0 = new double[2][9];
      MultiDirectionalSimplex multiDirectionalSimplex0 = null;
      try {
        multiDirectionalSimplex0 = new MultiDirectionalSimplex(doubleArray0, 1, 1.0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 9 != 1
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      double[] doubleArray0 = new double[1];
      NelderMeadSimplex nelderMeadSimplex0 = null;
      try {
        nelderMeadSimplex0 = new NelderMeadSimplex(doubleArray0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // equal vertices 0 and {1} in simplex configuration
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      NelderMeadSimplex nelderMeadSimplex0 = null;
      try {
        nelderMeadSimplex0 = new NelderMeadSimplex(0, 0);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // zero not allowed here
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test19()  throws Throwable  {
      NelderMeadSimplex nelderMeadSimplex0 = null;
      try {
        nelderMeadSimplex0 = new NelderMeadSimplex((double[]) null);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // null is not allowed
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }

  @Test(timeout = 4000)
  public void test20()  throws Throwable  {
      MultiDirectionalSimplex multiDirectionalSimplex0 = new MultiDirectionalSimplex(1);
      double[] doubleArray0 = new double[1];
      multiDirectionalSimplex0.build(doubleArray0);
      // Undeclared exception!
      try { 
        multiDirectionalSimplex0.iterate((MultivariateFunction) null, (Comparator<PointValuePair>) null);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.math3.optim.nonlinear.scalar.noderiv.AbstractSimplex", e);
      }
  }