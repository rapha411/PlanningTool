<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<sld:StyledLayerDescriptor version="1.0.0" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink">
  <sld:NamedLayer>
    <sld:Name>Housing_Projects</sld:Name>
    <sld:UserStyle>
      <sld:Name>Style1</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:FeatureTypeName>Housing_Projects</sld:FeatureTypeName>
        <sld:Rule>
          <sld:Name>Functieverandering Bedrijven/industrie</sld:Name>
          <sld:Title>Functieverandering Bedrijven/industrie</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering Bedrijven/industrie</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#B45FD2</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering Detailhandel</sld:Name>
          <sld:Title>Functieverandering Detailhandel</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering Detailhandel</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFA096</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering Kantoren</sld:Name>
          <sld:Title>Functieverandering Kantoren</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering Kantoren</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#EBC3D7</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering Maatschapelijk</sld:Name>
          <sld:Title>Functieverandering Maatschapelijk</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering Maatschapelijk</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#DC9B78</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering onbekend wat</sld:Name>
          <sld:Title>Functieverandering onbekend wat</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering onbekend wat</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#686868</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering overig</sld:Name>
          <sld:Title>Functieverandering overig</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering overig</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#EBE1EB</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Onbekend</sld:Name>
          <sld:Title>Onbekend</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Onbekend</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#B2B2B2</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Sloop/nieuwbouw (woningen)</sld:Name>
          <sld:Title>Sloop/nieuwbouw (woningen)</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Sloop/nieuwbouw (woningen)</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFFFB4</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Uitleggebied voor woningbouw</sld:Name>
          <sld:Title>Uitleggebied voor woningbouw</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Uitleggebied voor woningbouw</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFFF00</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Verdichtingslocatie</sld:Name>
          <sld:Title>Verdichtingslocatie</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Verdichtingslocatie</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFAA00</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
  <sld:NamedLayer>
    <sld:Name>Infrastructure_Investments</sld:Name>
    <sld:UserStyle>
      <sld:Name>Style1</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:FeatureTypeName>Infrastructure_Investments</sld:FeatureTypeName>
        <sld:Rule>
          <sld:Name>Bicycle</sld:Name>
          <sld:Title>Bicycle</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Modality</ogc:PropertyName>
              <ogc:Literal>Bicycle</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#007300</sld:CssParameter>
              <sld:CssParameter name="stroke-width">1.5</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:GraphicFill>
                <sld:Graphic>
                  <sld:Mark>
                    <sld:WellKnownName>cross</sld:WellKnownName>
                    <sld:Fill>
                      <sld:CssParameter name="fill">#267300</sld:CssParameter>
                      <sld:CssParameter name="fill-opacity">1.0</sld:CssParameter>
                    </sld:Fill>
                  </sld:Mark>
                  <sld:Size>12</sld:Size>
                </sld:Graphic>
              </sld:GraphicFill>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Bicycle - Bus - Boat</sld:Name>
          <sld:Title>Bicycle - Bus - Boat</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Modality</ogc:PropertyName>
              <ogc:Literal>Bicycle - Bus - Boat</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#4CE600</sld:CssParameter>
              <sld:CssParameter name="stroke-width">1.5</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:GraphicFill>
                <sld:Graphic>
                  <sld:Mark>
                    <sld:WellKnownName>cross</sld:WellKnownName>
                    <sld:Fill>
                      <sld:CssParameter name="fill">#00A9E6</sld:CssParameter>
                      <sld:CssParameter name="fill-opacity">1.0</sld:CssParameter>
                    </sld:Fill>
                  </sld:Mark>
                  <sld:Size>12</sld:Size>
                </sld:Graphic>
              </sld:GraphicFill>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Bus</sld:Name>
          <sld:Title>Bus</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Modality</ogc:PropertyName>
              <ogc:Literal>Bus</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#004DA8</sld:CssParameter>
              <sld:CssParameter name="stroke-width">1.5</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:GraphicFill>
                <sld:Graphic>
                  <sld:Mark>
                    <sld:WellKnownName>cross</sld:WellKnownName>
                    <sld:Fill>
                      <sld:CssParameter name="fill">#005CE6</sld:CssParameter>
                      <sld:CssParameter name="fill-opacity">1.0</sld:CssParameter>
                    </sld:Fill>
                  </sld:Mark>
                  <sld:Size>12</sld:Size>
                </sld:Graphic>
              </sld:GraphicFill>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Car</sld:Name>
          <sld:Title>Car</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Modality</ogc:PropertyName>
              <ogc:Literal>Car</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#FF0000</sld:CssParameter>
              <sld:CssParameter name="stroke-width">1.5</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:GraphicFill>
                <sld:Graphic>
                  <sld:Mark>
                    <sld:WellKnownName>cross</sld:WellKnownName>
                    <sld:Fill>
                      <sld:CssParameter name="fill">#FF0000</sld:CssParameter>
                      <sld:CssParameter name="fill-opacity">1.0</sld:CssParameter>
                    </sld:Fill>
                  </sld:Mark>
                  <sld:Size>12</sld:Size>
                </sld:Graphic>
              </sld:GraphicFill>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Car, Train, Bus, Bicycle</sld:Name>
          <sld:Title>Car, Train, Bus, Bicycle</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Modality</ogc:PropertyName>
              <ogc:Literal>Car, Train, Bus, Bicycle</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#A83800</sld:CssParameter>
              <sld:CssParameter name="stroke-width">1.5</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:GraphicFill>
                <sld:Graphic>
                  <sld:Mark>
                    <sld:WellKnownName>cross</sld:WellKnownName>
                    <sld:Fill>
                      <sld:CssParameter name="fill">#A83800</sld:CssParameter>
                      <sld:CssParameter name="fill-opacity">1.0</sld:CssParameter>
                    </sld:Fill>
                  </sld:Mark>
                  <sld:Size>12</sld:Size>
                </sld:Graphic>
              </sld:GraphicFill>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Train</sld:Name>
          <sld:Title>Train</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Modality</ogc:PropertyName>
              <ogc:Literal>Train</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000000</sld:CssParameter>
              <sld:CssParameter name="stroke-width">1.5</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:GraphicFill>
                <sld:Graphic>
                  <sld:Mark>
                    <sld:WellKnownName>cross</sld:WellKnownName>
                    <sld:Fill>
                      <sld:CssParameter name="fill">#686868</sld:CssParameter>
                      <sld:CssParameter name="fill-opacity">1.0</sld:CssParameter>
                    </sld:Fill>
                  </sld:Mark>
                  <sld:Size>12</sld:Size>
                </sld:Graphic>
              </sld:GraphicFill>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
  <sld:NamedLayer>
    <sld:Name>Housing_Projects_Total</sld:Name>
    <sld:UserStyle>
      <sld:Name>Style1</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:FeatureTypeName>Housing_Projects_Total</sld:FeatureTypeName>
        <sld:Rule>
          <sld:Name>Functieverandering Bedrijven/industrie</sld:Name>
          <sld:Title>Functieverandering Bedrijven/industrie</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering Bedrijven/industrie</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#B45FD2</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering Detailhandel</sld:Name>
          <sld:Title>Functieverandering Detailhandel</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering Detailhandel</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFA096</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering Kantoren</sld:Name>
          <sld:Title>Functieverandering Kantoren</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering Kantoren</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#EBC3D7</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering Maatschapelijk</sld:Name>
          <sld:Title>Functieverandering Maatschapelijk</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering Maatschapelijk</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#DC9B78</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering onbekend wat</sld:Name>
          <sld:Title>Functieverandering onbekend wat</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering onbekend wat</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#686868</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Functieverandering overig</sld:Name>
          <sld:Title>Functieverandering overig</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Functieverandering overig</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#EBE1EB</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Onbekend</sld:Name>
          <sld:Title>Onbekend</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Onbekend</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#B2B2B2</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Sloop/nieuwbouw (woningen)</sld:Name>
          <sld:Title>Sloop/nieuwbouw (woningen)</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Sloop/nieuwbouw (woningen)</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFFFB4</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Uitleggebied voor woningbouw</sld:Name>
          <sld:Title>Uitleggebied voor woningbouw</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Uitleggebied voor woningbouw</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFFF00</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Verdichtingslocatie</sld:Name>
          <sld:Title>Verdichtingslocatie</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>PLANTYP</ogc:PropertyName>
              <ogc:Literal>Verdichtingslocatie</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFAA00</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#6E6E6E</sld:CssParameter>
              <sld:CssParameter name="stroke-width">0.4</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
  <sld:NamedLayer>
    <sld:Name>Municipalities_NH</sld:Name>
    <sld:UserStyle>
      <sld:Name>Style1</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:FeatureTypeName>Municipalities_NH</sld:FeatureTypeName>
        <sld:Rule>
          <sld:Name>Municipalities_NH</sld:Name>
          <sld:Title>Municipalities_NH</sld:Title>
          <sld:PolygonSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#E1E1E1</sld:CssParameter>
              <sld:CssParameter name="stroke-width">3</sld:CssParameter>
              <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
          <sld:TextSymbolizer>
            <sld:Label>
              <ogc:PropertyName>GM_NAAM</ogc:PropertyName>
            </sld:Label>
            <sld:Font>
              <sld:CssParameter name="font-family">Arial</sld:CssParameter>
              <sld:CssParameter name="font-family">Sans-Serif</sld:CssParameter>
              <sld:CssParameter name="font-size">8</sld:CssParameter>
              <sld:CssParameter name="font-style">normal</sld:CssParameter>
              <sld:CssParameter name="font-weight">bold</sld:CssParameter>
            </sld:Font>
            <sld:Fill>
              <sld:CssParameter name="fill">#828282</sld:CssParameter>
              <sld:CssParameter name="fill-opacity">1.0</sld:CssParameter>
            </sld:Fill>
          </sld:TextSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>