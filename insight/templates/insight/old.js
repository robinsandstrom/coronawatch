// Add data
chart.data = [];

// Create axes
var valueAxisX = chart.xAxes.push(new am4charts.ValueAxis());
//valueAxisX.title.text = 'Dagar i framtiden';

// Create value axis
var valueAxisY = chart.yAxes.push(new am4charts.ValueAxis());
//valueAxisY.title.text = 'Antal smittade';
//valueAxisY.logarithmic = true;

valueAxisX.renderer.grid.template.disabled = true;
valueAxisY.renderer.grid.template.disabled = false;
valueAxisY.renderer.minGridDistance = 50;

// Create series
var lineSeries = chart.series.push(new am4charts.LineSeries());
lineSeries.dataFields.valueY = "ay";
lineSeries.dataFields.valueX = "ax";
lineSeries.strokeOpacity = 0;

var lineSeries2 = chart.series.push(new am4charts.LineSeries());
lineSeries2.dataFields.valueY = "by";
lineSeries2.dataFields.valueX = "bx";
lineSeries2.strokeOpacity = 1;
lineSeries2.fillOpacity = 0;
lineSeries2.fill = am4core.color(colors[1]); // red
lineSeries2.strokeWidth = 4;
lineSeries2.minBulletDistance = 10;
lineSeries2.tooltipText = "{value}";
lineSeries2.tooltip.pointerOrientation = "vertical";
lineSeries2.tooltip.background.cornerRadius = 20;
lineSeries2.tooltip.background.fillOpacity = 0.5;
lineSeries2.tooltip.label.padding(12,12,12,12)

// Create a range to change stroke for values below 0
var range = valueAxisY.createSeriesRange(lineSeries2);
range.value = health_cap;
range.endValue = 100000000;
range.contents.stroke = chart.colors.getIndex(4);
lineSeries2.fill = am4core.color(colors[1]); // red
range.contents.strokeOpacity = 0.7;
range.contents.fillOpacity = 0;


var med_cap = chart.series.push(new am4charts.LineSeries());
med_cap.dataFields.valueY = "cy";
med_cap.dataFields.valueX = "cx";
med_cap.strokeOpacity = 1;

// Add a bullet
var bullet = lineSeries.bullets.push(new am4charts.Bullet());

// Add a triangle to act as am arrow
var arrow = bullet.createChild(am4core.Circle);
arrow.horizontalCenter = "middle";
arrow.verticalCenter = "middle";
arrow.strokeWidth = 1;
arrow.strokeOpacity = 1;
arrow.stroke = chart.colors.getIndex(0);
arrow.fillOpacity = 0;
arrow.direction = "top";
arrow.width = 12;
arrow.height = 12;
// Add scrollbar
chart.scrollbarX = new am4charts.XYChartScrollbar();
chart.scrollbarX.series.push(lineSeries2);

// Add cursor
chart.cursor = new am4charts.XYCursor();
chart.cursor.xAxis = valueAxisX;
chart.cursor.snapToSeries = lineSeries2;
