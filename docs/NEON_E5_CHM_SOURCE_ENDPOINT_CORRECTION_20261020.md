# CHM source transport correction, before any actual raster pixel was read

The initial E5 pilot (Actions 39376646192; artifact 12243886073) recovered all 30 E5 reference points, but all 14 generic data/query requests returned no requested released block. No tile was downloaded and no canopy value was read. Its NO_RELEASED_TILE_AT_E5 category must therefore be read as a parser/source-access failure, NOT evidence that those locations lack imagery.

A source-only diagnostic at the NEON official tutorial site used the product's literal availableDataUrls, following the official NEON-utilities getFileUrls/byFileAOP code. The advertised monthly endpoint returned RELEASE-2026, month 2023-06, 278 files including 265 CHM GeoTIFFs. These files have size, crc32 and crc32c fields but null md5. The original CSV download helper's mandatory MD5 path was therefore inappropriate for this AOP schema. Evidence: Actions 39377416569; artifact 12243568034, SHA256 ffbae3d31970acba70d3eb702039a2f22fc33caa1400e62e08fc777bf17890aa. No raster values were examined in this diagnosis.

## Corrected source-access implementation

Use exactly the same original 30 plots, 14 sites and latest-advertised-month selection rule. Follow only the product's advertised NEON monthly URL, assert returned product/site/month and exact RELEASE-2026, then normalize only CHM file records. Require HTTPS, declared byte size and at least one recognized provider checksum. Verify every supplied recognized checksum (MD5 where present, CRC32 and/or CRC32C otherwise); compute local SHA256 separately for reproducibility. A local SHA256 is not described as a published provider MD5. A checksum missing or invalid in all supported fields causes STOP for that file, never silent acceptance.

This changes transport/schema handling only. It does not select another habitat year, relax coordinate CRS/mask checks, rotate trap coordinates, replace nodata with zero, or claim historical exposure or an environmental effect. The original failed access result remains archived alongside the new attempt. Actual GeoTIFF height values remain unopened at this amendment.

Official source: NEONScience/NEON-utilities, neonUtilities/R/byFileAOP.R and getFileUrls.R. The retrieved code uses the product's monthly availableDataUrls and checks the monthly response release; no arbitrary guessed raster URL is used here.
