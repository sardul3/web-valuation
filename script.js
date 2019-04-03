	function createTable()
	{
		var num_rows = document.getElementById('rows').value;
		var num_cols = document.getElementById('cols').value;
		var theader = '<table style="width:100%" class = "table table-bordered">\n';
		var tbody = '';

		for( var i=0; i<num_rows;i++)
		{
			tbody += '<tr>';
			for( var j=0; j<num_cols;j++)
			{
				if(i==0 && j==0){
					tbody += '<th width="30%">';
					tbody +='<textarea name ="'+i;
                    tbody += ''+j+'" id="'+i;
                    tbody += ''+j+'">Criteria</textarea>';
					tbody += '</th>';
				}
				else if(i==0 && j>0 && j<=num_cols-1){
					tbody += '<th>'
					tbody +='<textarea name ="'+i;
                    tbody += ''+j+'" id="'+i;
                    tbody += ''+j+'"></textarea>';
					tbody += '</th>';
				}
				/*else if(i==0 && j==num_cols-1){
					tbody += '<th>';
					tbody += 'Score';
					tbody += '</th>';
				}*/
				else{
				tbody += '<td height = "40%">';
				tbody +='<textarea name ="'+i;
                tbody += ''+j+'" id="'+i;
                tbody += ''+j+'"></textarea>';
				tbody += '</td>';
				}
			}
			tbody += '</tr>\n';
		}
		var tfooter = '</table>';
		var buttn = '<button class="btn btn-primary btn-lg  ">Add Rubric</button>';
		document.getElementById('rubricframe').innerHTML = theader + tbody + tfooter;
		document.getElementById('addrubric').innerHTML = buttn;
		
	}
