/*
Description: Quickly render datatables graph
Usage:
  <script>
    $(document).ready(function (){
        $.noConflict();

        // draw datatable
        var table = dt_init(
            selector="#example", // table id selector
            url = "/api/agent/data/users?as_datatables=true&inc_fields=id,email,active", // data url source
            dt_ajax=0, // 1=render columns manually (requires render_cols="col1,col2,col3", 0=render columns dynamically
            render_cols=0, // columns rendered (only used when dt_ajax=1)
            edit=1, // add a column with a edit icon
        )
    });
  </script>
*/
function draw_datatable(selector,url=0,data=0,dt_ajax=1,render_cols=0,edit=0) {
    var dt_json = {
        "columnDefs":[{'targets': 0,'width': "5%"}]
    };
    var edit_json = { // Icon for Actions
         'targets': -1,
         'searchable': false,
         'orderable': false,
         'width': "10%",
         'data': null,
         'render': function (data, type, row){
               var edit_url = window.location.href+"/edit/"+data[0];
               return '<td class="text-right"><a href='+edit_url+'><i class="tim-icons icon-settings"></i></a></td>'
         }
    };
    // Data source
    if (url) {
        dt_json["ajax"] = {"url":url} // ajax
        // Render column names
        if (render_cols) {
            var col = render_cols.split(",");
            $.each(col,function(i){
                $(selector+">thead>tr").append('<th>'+col[i]+'</th>');
            });
        };
    } else {
        dt_json["data"] = data // raw data
    }
    console.log(edit);
    // Append Edit button
    if (edit) {
        $(selector+">thead>tr").append("<th>edit</th>");
        dt_json["columnDefs"].push(edit_json);
    };
    // Draw table
    var table = $(selector).DataTable(dt_json);
    return table
}

function dt_init(selector,url,dt_ajax=1,render_cols=0,edit=0) {
    if (dt_ajax) {
        draw_datatable(selector,url=url,data=0,dt_ajax=1,render_cols=render_cols,edit=edit)
    } else {
        $.ajax({
             type: "GET",
             url: url,
             contentType: 'application/json',
             success: function(result) {
                 // Create columns for table based on data["columns"]
                 var columns = result["columns"];
                 $.each(columns,function(i) {
                     $(selector+">thead>tr").append('<th>'+columns[i]+'</th>');
                 });
                 draw_datatable(selector,url=0,data=result["data"],dt_ajax=0,render_cols=0,edit=edit)
             },
             error: function(result) {console.log(result);}
        });
    }
}

function ajax_method(url,method="POST",data={}) {
  $.ajax({
         type: method,
         url: url,
         data: data,
         contentType: 'application/json',
         success: function(result) {
            notify_call(result["message"],result["type"]);
         },
         error: function(result) {
            notify_call("Error","danger");
         }
   });
}
function notify_call(message,type) {
    $.notify({
      // options
      message: message
    },{
      // settings
      type: type
    });
}
