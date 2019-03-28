	function createTable()
	{
		var num_rows = document.getElementById('rows').value;
		var num_cols = document.getElementById('cols').value;
		var theader = '<table class = "table table-bordered table-responsive"> <thead> </thead>\n';
		theader += '<tr> <th scope="col">Criteria</th>';
		for(var i =0; i<=num_rows;i++){
			theader += `<th scope="col">${i+1}</th>`;
		}
		theader += "</tr>";
		var tbody = '';

		for( var i=0; i<num_rows;i++)
		{
			tbody += '<tr>';
			for( var j=0; j<num_cols;j++)
			{
				tbody += `<td contenteditable> <input type = "text" id= "category" name = ${i}${j}  />`;

				tbody += '</td>'
			}
			tbody += '</tr>\n';
		}
		var tfooter = '</table>';
		document.getElementById('rubricframe').innerHTML = theader + tbody + tfooter;
	}
