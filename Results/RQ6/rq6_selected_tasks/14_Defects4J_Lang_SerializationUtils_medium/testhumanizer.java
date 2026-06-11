@Test(timeout = 4000)
  public void testEOFExceptionOnDeserialization() throws Throwable {
      // Given: A serialized Integer object
      Integer integer = new Integer(2609);
      byte[] byteArray = SerializationUtils.serialize((Serializable) integer);
      ByteArrayInputStream byteArrayInputStream = new ByteArrayInputStream(byteArray, 2609, 2609);
      ClassLoader classLoader = ClassLoader.getSystemClassLoader();

      // When: Attempting to deserialize with an incorrect stream
      // Then: Expect EOFException
      try {
          new SerializationUtils.ClassLoaderAwareObjectInputStream(byteArrayInputStream, classLoader);
          fail("Expecting exception: EOFException");
      } catch (Throwable e) {
          verifyException("java.io.ObjectInputStream$PeekInputStream", e);
      }
  }

  @Test(timeout = 4000)
  public void testDeserializeNullByteArray() throws Throwable {
      // Given: A null byte array
      byte[] byteArray = null;

      // When: Attempting to deserialize a null byte array
      // Then: Expect IllegalArgumentException
      try {
          SerializationUtils.deserialize(byteArray);
          fail("Expecting exception: IllegalArgumentException");
      } catch (IllegalArgumentException e) {
          verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void testDeserializeIncompleteByteArray() throws Throwable {
      // Given: An incomplete byte array
      byte[] byteArray = new byte[2];

      // When: Attempting to deserialize an incomplete byte array
      // Then: Expect RuntimeException due to EOFException
      try {
          SerializationUtils.deserialize(byteArray);
          fail("Expecting exception: RuntimeException");
      } catch (RuntimeException e) {
          verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void testDeserializeNullInputStream() throws Throwable {
      // Given: A null InputStream
      InputStream inputStream = null;

      // When: Attempting to deserialize from a null InputStream
      // Then: Expect IllegalArgumentException
      try {
          SerializationUtils.deserialize(inputStream);
          fail("Expecting exception: IllegalArgumentException");
      } catch (IllegalArgumentException e) {
          verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void testSerializeAndDeserializeLocale() throws Throwable {
      // Given: A Locale object
      Locale locale = Locale.ENGLISH;

      // When: Serializing and then deserializing the Locale object
      byte[] byteArray = SerializationUtils.serialize((Serializable) locale);
      Locale deserializedLocale = (Locale) SerializationUtils.deserialize(byteArray);

      // Then: The deserialized Locale should match the original
      assertEquals("en", deserializedLocale.getLanguage());
  }

  @Test(timeout = 4000)
  public void testSerializeWithMockFileOutputStream() throws Throwable {
      // Given: An Integer object and a MockFileOutputStream
      Integer integer = new Integer(2734);
      MockFileOutputStream mockFileOutputStream = new MockFileOutputStream("org.apache.commons.lang3.SerializationException");

      // When: Attempting to serialize using a MockFileOutputStream
      // Then: Expect RuntimeException
      try {
          SerializationUtils.serialize((Serializable) integer, (OutputStream) mockFileOutputStream);
          fail("Expecting exception: RuntimeException");
      } catch (RuntimeException e) {
          verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void testSerializeWithUnconnectedPipe() throws Throwable {
      // Given: A Locale object and an unconnected PipedOutputStream
      Locale locale = Locale.ENGLISH;
      PipedOutputStream pipedOutputStream = new PipedOutputStream();
      DataOutputStream dataOutputStream = new DataOutputStream(pipedOutputStream);

      // When: Attempting to serialize using an unconnected pipe
      // Then: Expect RuntimeException
      try {
          SerializationUtils.serialize((Serializable) locale, (OutputStream) dataOutputStream);
          fail("Expecting exception: RuntimeException");
      } catch (RuntimeException e) {
          verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void testSerializeWithNullOutputStream() throws Throwable {
      // Given: An Integer object and a null OutputStream
      Integer integer = new Integer(-1584);
      OutputStream outputStream = null;

      // When: Attempting to serialize with a null OutputStream
      // Then: Expect IllegalArgumentException
      try {
          SerializationUtils.serialize((Serializable) integer, outputStream);
          fail("Expecting exception: IllegalArgumentException");
      } catch (IllegalArgumentException e) {
          verifyException("org.apache.commons.lang3.SerializationUtils", e);
      }
  }

  @Test(timeout = 4000)
  public void testCloneNullObject() throws Throwable {
      // Given: A null object
      Integer integer = null;

      // When: Cloning a null object
      Integer clonedInteger = SerializationUtils.clone(integer);

      // Then: The result should be null
      assertNull(clonedInteger);
  }

  @Test(timeout = 4000)
  public void testSerializationUtilsConstructor() throws Throwable {
      // Given: A new instance of SerializationUtils
      // When: Instantiating SerializationUtils
      SerializationUtils serializationUtils = new SerializationUtils();

      // Then: The instance should be created successfully
      assertNotNull(serializationUtils);
  }

  @Test(timeout = 4000)
  public void testCloneInteger() throws Throwable {
      // Given: An Integer object
      Integer integer = new Integer(-1584);

      // When: Cloning the Integer object
      Integer clonedInteger = SerializationUtils.clone(integer);

      // Then: The cloned Integer should match the original
      assertEquals(-1584, (int) clonedInteger);
  }