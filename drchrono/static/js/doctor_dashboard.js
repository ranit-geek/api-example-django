  $(document).ready(function() {

//  var timezone = jstz.determine();
//  var tzname = timezone.name();
//
//  Cookies.set('tzname_from_user', tzname);
  var csrf_token = $("#csrf_token_div").text().trim();
  var doctor_id = $("#doctor_id_div").text().trim();
  console.log(doctor_id)
    refresh(csrf_token, doctor_id);
  });


function call_patient(appointment_id, csrf_token) {
  // show 'seeing patient', remove timer, show Done button to complete appointment


  $('#btn_'+appointment_id).html('Finish');
  $('#btn_'+appointment_id).removeClass('btn-danger').addClass('btn-success');
  $('#btn_'+appointment_id).attr("onclick","appointment_completed(" + appointment_id + ", '"+ csrf_token +"')");

  $.post('/start_appointment/',
    {
      csrfmiddlewaretoken: csrf_token,
      appointment_id: appointment_id,

    },
    function(data){
      // data = $.parseJSON(data);
      if (data['msg'] == 'success'){
      }
      else{
        console.log(data['message']);
      }
    }
  );


}


function appointment_completed(appointment_id, csrf_token) {
  // update status of appointment to 'complete' in db and drchrono api

  $('#status_'+appointment_id).removeClass('alert-info').addClass('alert-warning');
  $('#status_'+appointment_id).html('<strong>Completed<strong/>');
  $('#btn_'+appointment_id).html('Completed').prop('disabled', true);;

  $.post('/complete_appointment/',
    {
      csrfmiddlewaretoken: csrf_token,
      appointment_id: appointment_id

    },
    function(data){
      // data = $.parseJSON(data);
      console.log(data);
    }
  );

}





function refresh(csrf_token, doctor_id) {
var url= doctor_id+'/update'
setInterval(function(){

  $.ajax({
        url: url,
        success: function(data) {
            $('#auto-refresh-body').html(data);
        }
    });

}, 15000);


}

