/*
Description: Quickly render chartjs graphs
Usage:
  <html>
    <body>
      <div class="row">
        <div class="col-lg-6">
          <div class="card card-chart">
            <div class="card-header">
              <h1 class="card-category">Card Header</h1>
              <h3 class="card-title"><i class="tim-icons icon-bulb-63 text-success"></i>Sub Header</h3>
            </div>
            <div class="card-body">
              <div class="chart-area">
                <canvas id="chart1"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
      <script>
        $(document).ready(function (){
            $.noConflict(); // remove if not needed

            // draw chartjs
            var table2 = cjs_init(
                selector="chart1",
                url="/api/agent/data/users?as_chartjs=true&groupby=email,count",
                type="bubble", // type of graph (line,pie,bar,doughnut,polarArea)
                graph_label="Testing", // header of graph
            );
        });
      </script>
    </body>
  </html>
*/

function draw_chartjs(selector,type,labels,values,graph_label="Graph") {
  new Chart(document.getElementById(selector), {
    type: type,
    data: {
      labels: labels,
      datasets: [{
        label: graph_label,
        borderColor: "white",
        borderWidth: 1,
        data: values
      }]
    },
    options: {
      responsive:true,
      maintainAspectRatio: false,
      animation: {
        duration: 3000
      },
      legend: {
        labels: {
          fontColor:"white"
        }
      },
      plugins: {
        colorschemes: {
          scheme: 'tableau.ClassicMedium10'
        }
      }
    }
  });
};

function cjs_init(selector,url,type,graph_label) {
    $.ajax({
        type: "GET",
        url: url,
        contentType: 'application/json',
        success: function(result) {
            draw_chartjs(selector,type,result["label"],result["data"],graph_label);
        },
        error: function(result) {console.log(result);}
    });
}
