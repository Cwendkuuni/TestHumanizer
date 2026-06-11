@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      PipedInputStream pipedInputStream0 = new PipedInputStream();
      ClassLoader classLoader0 = ClassLoader.getSystemClassLoader();
      SerializationUtils.ClassLoaderAwareObjectInputStream serializationUtils_ClassLoaderAwareObjectInputStream0 = null;
      try {
        serializationUtils_ClassLoaderAwareObjectInputStream0 = new SerializationUtils.ClassLoaderAwareObjectInputStream(pipedInputStream0, classLoader0);
        fail("Expecting exception: IOException");
      
      } catch(Throwable e) {
         //
         // Pipe not connected
         //
         verifyException("java.io.PipedInputStream", e);
      }
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      // Undeclared exception!
      try { 
        SerializationUtils.deserialize((byte[]) null);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // The byte[] must not be null
         //
         verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      PipedInputStream pipedInputStream0 = new PipedInputStream();
      // Undeclared exception!
      try { 
        SerializationUtils.deserialize((InputStream) pipedInputStream0);
        fail("Expecting exception: RuntimeException");
      
      } catch(RuntimeException e) {
         //
         // java.io.IOException: Pipe not connected
         //
         verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      // Undeclared exception!
      try { 
        SerializationUtils.deserialize((InputStream) null);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // The InputStream must not be null
         //
         verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      Class<Object> class0 = Object.class;
      ObjectStreamClass objectStreamClass0 = ObjectStreamClass.lookupAny(class0);
      byte[] byteArray0 = SerializationUtils.serialize((Serializable) objectStreamClass0);
      Object object0 = SerializationUtils.deserialize(byteArray0);
      assertNotSame(objectStreamClass0, object0);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      Integer integer0 = new Integer(363);
      MockFileOutputStream mockFileOutputStream0 = new MockFileOutputStream("VCFGV)3|9NEp|4b", false);
      // Undeclared exception!
      try { 
        SerializationUtils.serialize((Serializable) integer0, (OutputStream) mockFileOutputStream0);
        fail("Expecting exception: RuntimeException");
      
      } catch(RuntimeException e) {
         //
         // org.evosuite.runtime.mock.java.lang.MockThrowable: Error in writing to file
         //
         verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      Class<Object> class0 = Object.class;
      PipedOutputStream pipedOutputStream0 = new PipedOutputStream();
      // Undeclared exception!
      try { 
        SerializationUtils.serialize((Serializable) class0, (OutputStream) pipedOutputStream0);
        fail("Expecting exception: RuntimeException");
      
      } catch(RuntimeException e) {
         //
         // java.io.IOException: Pipe not connected
         //
         verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      // Undeclared exception!
      try { 
        SerializationUtils.serialize((Serializable) (byte)16, (OutputStream) null);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // The OutputStream must not be null
         //
         verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      Integer integer0 = SerializationUtils.clone((Integer) null);
      assertNull(integer0);
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      SerializationUtils serializationUtils0 = new SerializationUtils();
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      Integer integer0 = new Integer(21);
      Integer integer1 = SerializationUtils.clone(integer0);
      assertTrue(integer1.equals((Object)integer0));
  }