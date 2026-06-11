@Test(timeout = 4000)
  public void test0()  throws Throwable  {
      AddressToUsAddressFunctor addressToUsAddressFunctor0 = new AddressToUsAddressFunctor();
      AddressDetails addressDetails0 = new AddressDetails();
      GeoAddress geoAddress0 = new GeoAddress();
      geoAddress0.setAddressDetails(addressDetails0);
      GeoAltitude geoAltitude0 = new GeoAltitude();
      GeoCoordinate geoCoordinate0 = new GeoCoordinate((-2596.9698), 0.0, geoAltitude0);
      geoAddress0.setCoordinate(geoCoordinate0);
      GeoUsAddress geoUsAddress0 = addressToUsAddressFunctor0.execute(geoAddress0);
      assertEquals("", geoUsAddress0.getCountry());
  }

  @Test(timeout = 4000)
  public void test1()  throws Throwable  {
      AddressToUsAddressFunctor addressToUsAddressFunctor0 = new AddressToUsAddressFunctor();
      AddressDetails addressDetails0 = new AddressDetails();
      AddressDetails.Country addressDetails_Country0 = new AddressDetails.Country();
      addressDetails0.setCountry(addressDetails_Country0);
      GeoAddress geoAddress0 = new GeoAddress();
      geoAddress0.setAddressDetails(addressDetails0);
      // Undeclared exception!
      try { 
        addressToUsAddressFunctor0.execute(geoAddress0);
        fail("Expecting exception: NoClassDefFoundError");
      
      } catch(NoClassDefFoundError e) {
         //
         // org/apache/commons/collections/CollectionUtils
         //
         verifyException("geo.google.mapping.AddressToUsAddressFunctor", e);
      }
  }

  @Test(timeout = 4000)
  public void test2()  throws Throwable  {
      AddressToUsAddressFunctor addressToUsAddressFunctor0 = AddressToUsAddressFunctor.getInstance();
      assertNotNull(addressToUsAddressFunctor0);
  }

  @Test(timeout = 4000)
  public void test3()  throws Throwable  {
      AddressToUsAddressFunctor addressToUsAddressFunctor0 = new AddressToUsAddressFunctor();
      AddressDetails addressDetails0 = new AddressDetails();
      GeoAddress geoAddress0 = new GeoAddress();
      geoAddress0.setAddressDetails(addressDetails0);
      GeoUsAddress geoUsAddress0 = addressToUsAddressFunctor0.execute(geoAddress0);
      assertEquals(GeoAddressAccuracy.UNKNOWN_LOCATION, geoUsAddress0.getAccuracy());
  }