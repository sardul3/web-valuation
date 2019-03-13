	function createTable()
	{
		var num_rows = document.getElementById('rows').value;
		var num_cols = document.getElementById('cols').value;
		var theader = '<table class = "table table-bordered">\n';
		var tbody = '';

		for( var i=0; i<num_rows;i++)
		{
			tbody += '<tr>';
			for( var j=0; j<num_cols;j++)
			{
				tbody += '<td contenteditable>';
				tbody += 'Cell ' + i + ',' + j;
				tbody += '</td>'
			}
			tbody += '</tr>\n';
		}
		var tfooter = '</table>';
		document.getElementById('rubricframe').innerHTML = theader + tbody + tfooter;
	}