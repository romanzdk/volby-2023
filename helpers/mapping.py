import folium
import streamlit.components.v1 as components


# For some reason I was not able to render legend using default Geopandas.explore()
# So I had to hack it this way


def folium_static(
	fig: folium.Map,
	colors: list[str],
	labels: list[str],
	title: str,
	width: int = 700,
	height: int = 500,
) -> components.html:
	fig = folium.Figure().add_child(fig)
	fig = add_categorical_legend(fig, title, colors = colors, labels = labels)
	return components.html(fig.render(), height = (fig.height or height) + 10, width = width)


def add_categorical_legend(
	folium_map: folium.Figure,
	title: str,
	colors: list[str],
	labels: list[str],
) -> folium.Figure:
	if len(colors) != len(labels):
		raise ValueError('colors and labels must have the same length.')

	color_by_label = dict(zip(labels, colors))

	legend_categories = ''
	for label, color in color_by_label.items():
		legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"

	legend_html = f'''
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    '''
	script = f'''
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      '''

	css = '''

    <style type='text/css'>
      .maplegend {
      position: relative;
      z-index:9999;
      border:2px solid grey;
      background-color:rgba(255, 255, 255, 0.8);
      border-radius:6px;
      padding: 10px;
      font-size:14px;
      right: 20px;
      top: 20px;
      float:right;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 18px;
        width: 18px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    '''

	folium_map.get_root().header.add_child(folium.Element(script + css))

	return folium_map
