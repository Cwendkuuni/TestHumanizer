@Test(timeout = 4000)
  public void test00()  throws Throwable  {
      String[] stringArray0 = new String[5];
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, (Map<String, Integer>) null, "tP,", 0L);
      Iterator<String> iterator0 = cSVRecord0.iterator();
      assertNotNull(iterator0);
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      String[] stringArray0 = new String[7];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "i", 0L);
      boolean boolean0 = cSVRecord0.isMapped("%_f");
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      String[] stringArray0 = new String[4];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      Integer integer0 = new Integer(1);
      hashMap0.put("", integer0);
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "", (-1L));
      HashMap<String, String> hashMap1 = new HashMap<String, String>();
      cSVRecord0.putIn(hashMap1);
      assertEquals((-1L), cSVRecord0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      String[] stringArray0 = new String[4];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      Integer integer0 = new Integer(3);
      hashMap0.put("mS<~sV", integer0);
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "mS<~sV", 3);
      boolean boolean0 = cSVRecord0.isSet("mS<~sV");
      assertEquals(3L, cSVRecord0.getRecordNumber());
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      Integer integer0 = new Integer(3737);
      hashMap0.put("(*@X", integer0);
      CSVRecord cSVRecord0 = new CSVRecord((String[]) null, hashMap0, "(*@X", 0L);
      boolean boolean0 = cSVRecord0.isSet("(*@X");
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord((String[]) null, hashMap0, "(*@X", 0L);
      boolean boolean0 = cSVRecord0.isSet("(*@X");
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      String[] stringArray0 = new String[0];
      String string0 = "Ma<!\\uB`>]a=GuOv)P";
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, (Map<String, Integer>) null, string0, (-54L));
      boolean boolean0 = cSVRecord0.isSet(string0);
      assertEquals((-54L), cSVRecord0.getRecordNumber());
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      String[] stringArray0 = new String[3];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "vMf'S',jU", (-1083L));
      boolean boolean0 = cSVRecord0.isConsistent();
      assertEquals((-1083L), cSVRecord0.getRecordNumber());
      assertFalse(boolean0);
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      CSVRecord cSVRecord0 = new CSVRecord((String[]) null, (Map<String, Integer>) null, "tLiI4Nn", 0L);
      boolean boolean0 = cSVRecord0.isConsistent();
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      String[] stringArray0 = new String[0];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "~DaTFT?:@[7D>", 0L);
      boolean boolean0 = cSVRecord0.isConsistent();
      assertTrue(boolean0);
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      String[] stringArray0 = new String[3];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      Integer integer0 = new Integer(3);
      hashMap0.put("mS<~sV", integer0);
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "mS<~sV", 3);
      // Undeclared exception!
      try { 
        cSVRecord0.get("mS<~sV");
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // Index for header 'mS<~sV' is 3 but CSVRecord only has 3 values!
         //
         verifyException("org.apache.commons.csv.CSVRecord", e);
      }
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      CSVRecord cSVRecord0 = new CSVRecord((String[]) null, (Map<String, Integer>) null, "Rp>=W_j@'4a'35HYdE", 3357L);
      // Undeclared exception!
      try { 
        cSVRecord0.get("Rp>=W_j@'4a'35HYdE");
        fail("Expecting exception: IllegalStateException");
      
      } catch(IllegalStateException e) {
         //
         // No header mapping was specified, the record values can't be accessed by name
         //
         verifyException("org.apache.commons.csv.CSVRecord", e);
      }
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      String[] stringArray0 = new String[3];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "mS<~sV", 3);
      // Undeclared exception!
      try { 
        cSVRecord0.get("mS<~sV");
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // Mapping for mS<~sV not found, expected one of []
         //
         verifyException("org.apache.commons.csv.CSVRecord", e);
      }
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      CSVRecord cSVRecord0 = new CSVRecord((String[]) null, (Map<String, Integer>) null, "tLiI4Nn", 0L);
      int int0 = cSVRecord0.size();
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      CSVRecord cSVRecord0 = new CSVRecord((String[]) null, (Map<String, Integer>) null, "Rp>=W_j@'4a'35HYdE", 3357L);
      long long0 = cSVRecord0.getRecordNumber();
      assertEquals("[]", cSVRecord0.toString());
      assertEquals(3357L, long0);
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      String[] stringArray0 = new String[3];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "wwkTs$4lt", (-24L));
      // Undeclared exception!
      try { 
        cSVRecord0.get((-4));
        fail("Expecting exception: ArrayIndexOutOfBoundsException");
      
      } catch(ArrayIndexOutOfBoundsException e) {
         //
         // -4
         //
         verifyException("org.apache.commons.csv.CSVRecord", e);
      }
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      String[] stringArray0 = new String[3];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "", (-1L));
      String[] stringArray1 = cSVRecord0.values();
      assertEquals((-1L), cSVRecord0.getRecordNumber());
      assertEquals(3, stringArray1.length);
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      String[] stringArray0 = new String[7];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, stringArray0[1], (-249L));
      String string0 = cSVRecord0.toString();
      assertEquals("[null, null, null, null, null, null, null]", string0);
      assertEquals((-249L), cSVRecord0.getRecordNumber());
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      String[] stringArray0 = new String[2];
      HashMap<String, Integer> hashMap0 = new HashMap<String, Integer>();
      CSVRecord cSVRecord0 = new CSVRecord(stringArray0, hashMap0, "mSJ<DsVN", 1446L);
      cSVRecord0.toMap();
      assertEquals(1446L, cSVRecord0.getRecordNumber());
      assertEquals("[null, null]", cSVRecord0.toString());
  }

  @Test(timeout = 4000)
  public void test19()  throws Throwable  {
      CSVRecord cSVRecord0 = new CSVRecord((String[]) null, (Map<String, Integer>) null, "tLiI4Nn", 0L);
      cSVRecord0.getComment();
      assertEquals("[]", cSVRecord0.toString());
  }