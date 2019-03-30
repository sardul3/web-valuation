



function addRow() {
  var tbl = document.getElementById("rubricbase");
  var row = tbl.insertRow(tbl.rows.length);
  var i;
  for (i=0; i<tbl.rows[0].cells.length; i++){
     createCell(row.insertCell(i),'row');
  }
}

function createCell(cell, style){

    var tablecell = document.createElement('input');
    tablecell.setAttribute('name', 'measure')

    tablecell.setAttribute('type', 'text');
    cell.appendChild(tablecell);
    tablecell.contentEditable = 'true';
    n=n+1;
}



function addColumn(){
    var tbl = document.getElementById("rubricbase");
    var i;
    for (i=0; i<tbl.rows.length; i++){
        createCell(tbl.rows[i].insertCell(tbl.rows[i].cells.length-1),'contentEditable=true;');
    }
}

function deleteColumns(){
    var tbl = document.getElementById("rubricbase");
    var totalCols = tbl.rows[0].cells.length-1;
    var i;

    for(i=0; i<tbl.rows.length; i++){
        if(totalCols>=2){
            tbl.rows[i].deleteCell(totalCols-1);
        }

    }


}

function deleteRows(){
    var tbl = document.getElementById("rubricbase");
    var lastRow = tbl.rows.length-1;
    if(lastRow>1){
        tbl.deleteRow(lastRow);
    }
    else{
        document.getElementById("deleteRows").disabled = true;
    }


}
