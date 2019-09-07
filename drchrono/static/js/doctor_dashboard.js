function add() {
    seconds++;
    if (seconds >= 60) {
        seconds = 0;
        minutes++;
        if (minutes >= 60) {
            minutes = 0;
            hours++;
        }
    }

    h1.textContent = (hours ? (hours > 9 ? hours : "0" + hours) : "00") + ":" + (minutes ? (minutes > 9 ? minutes : "0" + minutes) : "00") + ":" + (seconds > 9 ? seconds : "0" + seconds);

    timer();
}

function timer() {
    t = setTimeout(add, 1000);
}


function call_patient(appointment_id, csrf_token) {
  // show 'seeing patient', remove timer, show Done button to complete appointment
  $('#timer_'+appointment_id).remove();
  $('#status_'+appointment_id).removeClass('alert-success').addClass('alert-info');
  $('#status_'+appointment_id).html('<strong>In Progress<strong/>');
  $('#btn_'+appointment_id).html('Done');
  $('#btn_'+appointment_id).removeClass('btn-success').addClass('btn-info');
  $('#btn_'+appointment_id).attr("onclick","appointment_completed(" + appointment_id + ", '"+ csrf_token +"')");

  var current_date_time = new Date($.now());
  current_date_time = current_date_time.toUTCString()
  console.log(current_date_time);
  // add time_waited duration to appointment_obj and save in db

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
  $('#btn_'+appointment_id).remove();

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
