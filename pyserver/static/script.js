onClick = function(){

	/// Get the parameters from the feilds 
	// params = { 
	// "blat":$("#blat").val(),
	// "blong":$("#blong").val(),
	// "elat":$("#elat").val(),
	// "elong":$("#elong").val()}

	/// These parameters are for debugging 
	params = { 
	"blat":38.957060,
	"blong":-77.068804,
	"elat":38.909924,
	"elong": -77.039964}

	start_lat_val = params['blat']
    start_lng_val = params['blong']
    end_lat_val = params['elat']
    end_lng_val = params['elong']

    // These variables are used for the Uber aPI 
    start_lat = "start_latitude=" + start_lat_val
    start_lng = "start_longitude=" + start_lng_val
    end_lat = "end_latitude=" + end_lat_val
    end_lng = "end_longitude=" + end_lng_val

    /// Stored API keys ( should really go somewhere else )
    uber_key = "server_token=27-zMQ7EpycOjn_qFBMWuI6Vb0QYJ6gcpPbaL5bE"
    google_key = "&key=AIzaSyD6DiPM0cuIqaEfa6Bk-fmp8oRW6UG2uUY" 

    /// These littler url will be appended to a larger URL in ihe api call 
    uber_lil_url = String(start_lat + "&" + start_lng + "&" + end_lat + "&" + end_lng + "&" + uber_key)
	google_lil_url = String("origin=" + start_lat_val + "+" + start_lng_val +"&destination=" + end_lat_val + "+" + end_lng_val + '&mode=transit' + google_key)


	//// Get the Uber Estimation for the Trip 
	var UbersearchReq = $.get("/uber_get_estimates/" + uber_lil_url);
    UbersearchReq.done(function(data) {
      //$("#url").attr("href", data.result);
      //console.log(data)
      document.getElementById("uber_result").innerHTML = data["prices"][0]['estimate'];
    });

    // Get the Google Estimation for the Trip 
    var GooglesearchReq = $.get("/google_get_estimates/" + google_lil_url);
    GooglesearchReq.done(function(data) {
      //$("#url").attr("href", data.result);
      var steps = data["routes"][0]['legs'][0]['steps']

      var price = 0;

      for (i = 0; i < steps.length - 1; i++)
      {
      	step = steps[i]

      	if (step['travel_mode'] == 'TRANSIT')
      	{
      		if (step['html_instructions'].toLowerCase().indexOf("bus") > -1)
      		{

      			price += 1.75 
      		}
      		else if (step['html_instructions'].toLowerCase().indexOf("rail") > -1)
      		{
      			peak = false;

      			if (peak){
      				price += 5.90
      			}
      			else{
      				price += 3.60
      			}
      		}
      	}

      }


      document.getElementById("google_result").innerHTML = "$"  + String(price);

      /// now i want to get the cost estimation for the uber trips ( top 5???? )

    });

};

$(document).ready(function() {

  $("#search").click( onClick);

});


