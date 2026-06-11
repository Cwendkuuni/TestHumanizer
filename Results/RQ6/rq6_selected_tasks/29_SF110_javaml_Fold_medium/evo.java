@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[4];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      int int0 = fold0.size();
      assertEquals(4, int0);
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[8];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      Iterator<Instance> iterator0 = fold0.iterator();
      assertNotNull(iterator0);
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[9];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      // Undeclared exception!
      try { 
        fold0.instance(865);
        fail("Expecting exception: ArrayIndexOutOfBoundsException");
      
      } catch(ArrayIndexOutOfBoundsException e) {
         //
         // 865
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      LinkedHashSet<Instance> linkedHashSet0 = new LinkedHashSet<Instance>();
      double[] doubleArray0 = new double[3];
      DenseInstance denseInstance0 = new DenseInstance(doubleArray0, linkedHashSet0);
      Instance instance0 = denseInstance0.minus(2.0);
      linkedHashSet0.add(instance0);
      DefaultDataset defaultDataset0 = new DefaultDataset(linkedHashSet0);
      int[] intArray0 = new int[5];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      DefaultDataset defaultDataset1 = (DefaultDataset)fold0.copy();
      assertEquals("[{[-2.0, -2.0, -2.0];null}, {[-2.0, -2.0, -2.0];null}, {[-2.0, -2.0, -2.0];null}, {[-2.0, -2.0, -2.0];null}, {[-2.0, -2.0, -2.0];null}]", defaultDataset1.toString());
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[5];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      Object[] objectArray0 = new Object[8];
      DenseInstance denseInstance0 = new DenseInstance(14);
      defaultDataset0.add((Instance) denseInstance0);
      Object[] objectArray1 = fold0.toArray(objectArray0);
      assertEquals(8, objectArray1.length);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[1];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      // Undeclared exception!
      try { 
        fold0.toArray();
        fail("Expecting exception: ArrayIndexOutOfBoundsException");
      
      } catch(ArrayIndexOutOfBoundsException e) {
         //
         // Array index out of range: 0
         //
         verifyException("java.util.Vector", e);
      }
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      Fold.FoldIterator fold_FoldIterator0 = fold0.new FoldIterator(357);
      boolean boolean0 = fold_FoldIterator0.hasPrevious();
      assertTrue(boolean0);
      assertEquals(357, fold_FoldIterator0.previousIndex());
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      Fold.FoldIterator fold_FoldIterator0 = fold0.new FoldIterator();
      boolean boolean0 = fold_FoldIterator0.hasPrevious();
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.remove(32);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.remove((Object) defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.contains(defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Method is not yet implemented
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.set(2792, (Instance) null);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.containsAll(defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Method is not yet implemented
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[1];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      // Undeclared exception!
      try { 
        fold0.removeAll(defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.add((Instance) null);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Cannot do this on a fold of a dataset
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.clear();
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Cannot do this on a fold of a dataset
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      int int0 = fold0.noAttributes();
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.get(56);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      NormalizedEuclideanSimilarity normalizedEuclideanSimilarity0 = new NormalizedEuclideanSimilarity(fold0);
      // Undeclared exception!
      try { 
        fold0.kNearest(366, (Instance) null, normalizedEuclideanSimilarity0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Method is not yet implemented
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test19()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.lastIndexOf(defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Method is not yet implemented
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test20()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[0];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      boolean boolean0 = defaultDataset0.addAll((Collection<? extends Instance>) fold0);
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test21()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[5];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      Object object0 = fold0.classValue((-1974));
      assertNull(object0);
  }

  @Test(timeout = 4000)
  public void test22()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      ListIterator<Instance> listIterator0 = fold0.listIterator(28);
      assertTrue(listIterator0.hasPrevious());
  }

  @Test(timeout = 4000)
  public void test23()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.indexOf(defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Method is not yet implemented
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test24()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.addAll(4, (Collection<? extends Instance>) defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Cannot do this on a fold of a dataset
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test25()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[1];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      // Undeclared exception!
      try { 
        fold0.addAll((Collection<? extends Instance>) defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Cannot do this on a fold of a dataset
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test26()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      MockRandom mockRandom0 = new MockRandom();
      // Undeclared exception!
      try { 
        fold0.folds(0, mockRandom0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Method is not yet implemented
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test27()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.subList(227, 227);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test28()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      // Undeclared exception!
      try { 
        fold0.classIndex(defaultDataset0);
        fail("Expecting exception: ClassCastException");
      
      } catch(ClassCastException e) {
         //
         // net.sf.javaml.core.DefaultDataset cannot be cast to java.lang.Comparable
         //
         verifyException("java.util.TreeMap", e);
      }
  }

  @Test(timeout = 4000)
  public void test29()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      SortedSet<Object> sortedSet0 = fold0.classes();
      assertTrue(sortedSet0.isEmpty());
  }

  @Test(timeout = 4000)
  public void test30()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[1];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      // Undeclared exception!
      try { 
        fold0.retainAll(defaultDataset0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test31()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      SparseInstance sparseInstance0 = new SparseInstance(1);
      // Undeclared exception!
      try { 
        fold0.add(1, (Instance) sparseInstance0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // Cannot do this on a fold of a dataset
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test32()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      boolean boolean0 = fold0.isEmpty();
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test33()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[6];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      Fold.FoldIterator fold_FoldIterator0 = fold0.new FoldIterator();
      int int0 = fold_FoldIterator0.previousIndex();
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test34()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      Fold.FoldIterator fold_FoldIterator0 = fold0.new FoldIterator();
      double[] doubleArray0 = new double[2];
      DenseInstance denseInstance0 = new DenseInstance(doubleArray0, fold_FoldIterator0);
      // Undeclared exception!
      try { 
        fold_FoldIterator0.add((Instance) denseInstance0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold$FoldIterator", e);
      }
  }

  @Test(timeout = 4000)
  public void test35()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      Fold.FoldIterator fold_FoldIterator0 = fold0.new FoldIterator(9);
      // Undeclared exception!
      try { 
        fold_FoldIterator0.previous();
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("net.sf.javaml.core.Fold", e);
      }
  }

  @Test(timeout = 4000)
  public void test36()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      int[] intArray0 = new int[5];
      Fold fold0 = new Fold(defaultDataset0, intArray0);
      Fold.FoldIterator fold_FoldIterator0 = fold0.new FoldIterator();
      int int0 = fold_FoldIterator0.nextIndex();
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test37()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      Fold.FoldIterator fold_FoldIterator0 = fold0.new FoldIterator();
      // Undeclared exception!
      try { 
        fold_FoldIterator0.remove();
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold$FoldIterator", e);
      }
  }

  @Test(timeout = 4000)
  public void test38()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      Fold.FoldIterator fold_FoldIterator0 = fold0.new FoldIterator();
      double[] doubleArray0 = new double[0];
      SparseInstance sparseInstance0 = new SparseInstance(doubleArray0, defaultDataset0);
      // Undeclared exception!
      try { 
        fold_FoldIterator0.set((Instance) sparseInstance0);
        fail("Expecting exception: UnsupportedOperationException");
      
      } catch(UnsupportedOperationException e) {
         //
         // You cannot do this on a fold.
         //
         verifyException("net.sf.javaml.core.Fold$FoldIterator", e);
      }
  }

  @Test(timeout = 4000)
  public void test39()  throws Throwable  {
      DefaultDataset defaultDataset0 = new DefaultDataset();
      Fold fold0 = new Fold(defaultDataset0, (int[]) null);
      ListIterator<Instance> listIterator0 = fold0.listIterator();
      assertFalse(listIterator0.hasPrevious());
  }