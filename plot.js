
var plot = function(id, data) {

  // var data = [2724.91221331707, 2737.74623109829, 2618.41673570888, 2606.8632352265, 2488.19416337737, 2531.34899878484, 2575.43777025493, 2573.94083813652, 2552.32037388414];

  var margin = {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    },
    width = 100 - margin.left - margin.right,
    height = 40 - margin.top - margin.bottom;

  var x = d3.scale.linear()
    .domain([0, data.length - 1])
    .range([0, width]);

  var y = d3.scale.linear()
    .domain([d3.min(data), d3.max(data)])
    .range([height, 0]);

  var xAxis = d3.svg.axis()
    .scale(x)
    // .tickSize(-height)
    .orient("bottom");
  // .tickSubdivide(true);

  // var xAxis = d3.svg.axis()
  //     .scale(x)
  //     .orient("bottom");

  var yAxis = d3.svg.axis()
    .scale(y)
    .ticks(4)
    .orient("left")
    .tickFormat(function(d, i) {
      return d + '$'
    });

  var area = d3.svg.area()
    .interpolate("monotone")
    .x(function(d, i) {
      return x(i);
    })
    .y0(height)
    .y1(function(d) {
      return y(d);
    })

  var svg = d3.select("svg#" + id)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("path")
    .datum(data)
    .attr("class", "area")
    .attr("d", area);

  svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);

  svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
    .selectAll("text")
    .style("text-anchor", "end")
    .attr("dx", "2.2em")
    .attr("dy", "-1em")
    .attr("transform", function(d) {
      return "rotate(-75)"
    });
}