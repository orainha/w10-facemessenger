// Credits to:
// Chase Allen, author of "convertArrayOfObjectsToCSV", and "downloadCSV" functions
// site: https://www.developintelligence.com/blog/2017/04/use-javascript-to-export-your-data-as-csv/ 
// w3schools.com - JavaScript and HTML DOM Reference
// site: https://www.w3schools.com/jsref/

(function(){
    'use strict'
    var btn_export = document.getElementById('export_csv')


    function convertArrayOfObjectsToCSV(args) 
    {
        var result, ctr, keys, columnDelimiter, lineDelimiter, data;
        
        data = args.data || null;
        if (data == null || !data.length) {
        return null;
        }
        
        columnDelimiter = args.columnDelimiter || ',';
        lineDelimiter = args.lineDelimiter || '\n';
        
        keys = Object.keys(data[0]);
        
        result = '';
        result += keys.join(columnDelimiter);
        result += lineDelimiter;
        
        data.forEach(function(item) {
        ctr = 0;
        keys.forEach(function(key) {
        if (ctr > 0) result += columnDelimiter;
        
        result += item[key];
        ctr++;
        });
        result += lineDelimiter;
        });
        
        return result;
    }

    function downloadCSV(args) 
    {
        var data, filename, link;
        var csv = convertArrayOfObjectsToCSV({
        data: args.data
        });
        if (csv == null) return;
        
        filename = args.filename || 'export.csv';
        

        if (!csv.match(/^data:text\/csv/i)) {
            csv = 'data:text/csv;charset=utf-8,' + csv;
        }
        
        data = encodeURI(csv);
        
        // ---------------------------------
        // solving latin characters encoding
        
        //replace the space character
        //data = csv.replace(/ /g,"%20")

        //replace the newline character
        //data = data.replace("\n","%0A")
        
        //console.log(data)
        
        //replace bytes for 'é' character
        // var index
        // if (data.search("%C3%A3") > 0)
        //     console.log("found")
        //     console.log(data.replace("%C3%A9","é"))
            // if(index = data.search("é") > 0)
            //     console.log("found on: "+index)
            //     console.log(data)

        // -------------------------------
        
        
        link = document.createElement('a');
        link.setAttribute('href', data);
        link.setAttribute('download', filename);
        link.click();
        
    }
   
    var exportCSV=function()
    {
        //console.log("hello")
        var table_rows = document.getElementsByTagName("tr")
        
        var csv_data = []   
        var fieldnames = []
        var row = {}
        for (var i=0; i<table_rows.length; i++)
        {    
            //get the field names, they will be the object properties keys                        
            if (i == 0)
            {
                //we are on first row: <th>
                var cells = table_rows[i].cells
                for (var j=0; j<cells.length; j++)
                {
                    fieldnames[j] = cells[j].innerText
                }
                continue;
            }
            else{
                row = {}
                var cells = table_rows[i].cells
                for (var j=0; j<cells.length; j++)
                {
                    //if is image field, needs special treatment             
                    var start_img_index
                    if ((start_img_index = cells[j].innerHTML.search("<img src=\"")) > 0)
                    {
                        var img_url = cells[j].firstElementChild.attributes.href.value;
                        //console.log("image: " + img_url)
                        row[fieldnames[j]] = img_url
                    }else
                    {
                        row[fieldnames[j]] = cells[j].innerText
                    }
                }
            }
            
            //insert row data on csv data array
            csv_data[i-1] = row            
        }

        //insert data on functions to download csv file
        var obj = {filename : 'export.csv', data: csv_data}
        downloadCSV(obj)
    }

    
    btn_export.addEventListener('click', exportCSV);

 })();