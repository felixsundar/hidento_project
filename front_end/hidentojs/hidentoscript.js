$(function() {
   $("#edit_crush_deleteButton").click(function(){
      if (confirm("If you are matched with this crush currently, your match will be broken.\n\nAre you sure you want to delete?")){
         $('form#edit_crush_deleteForm').submit();
      } else{
      event.preventDefault();
      }
   });
});

$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

$(document).ready(function() {
   $("#instagramVerify").click(function(){
      var instagramUsername = $("#id_crushUsername").val();
      if (!instagramUsername.trim() || instagramUsername.length == 0){
        alert("Enter an Instagram username to verify.");
      } else if (hasWhiteSpace(instagramUsername.trim())){
        alert("Instagram username should not contain spaces.")
      } else if (hasatsymbol(instagramUsername.trim())){
        alert("Do not include '@' in Instagram username.")
      } else{
        instagramLink = "https://www.instagram.com/" + instagramUsername.trim();
        window.open(instagramLink, '_blank')
      }
   });
});

function hasatsymbol(s) {
  return s.indexOf('@') >= 0;
}

function hasWhiteSpace(s) {
  return s.indexOf(' ') >= 0;
}

$(function()
{
  $("#hidentoform").submit(function(){
    $("input[type='submit']", this)
      .val("Please Wait...")
      .attr("disabled", true);
    return true;
  });
});

$(".edit_crush_activeClass").change(function() {
    if(!this.checked && this.defaultChecked) {
        alert("You are about to deactivate this crush.\n\nIf you are matched with this crush currently, your match will be broken.")
    }
});

$(function() {
   $(".sentMessageDeleteButton").click(function(){
      if (confirm("The receiver will not be able to see this message.\n\nAre you sure you want to delete?")){
         $(this).submit();
      } else{
      event.preventDefault();
      }
   });
});

$(function() {
   $(".receivedMessageHideButton").click(function(){
      if (confirm("You won't be able to see this message again.\n\nAre you sure you want to hide it?")){
         $(this).submit();
      } else{
      event.preventDefault();
      }
   });
});

$(function() {
   $(".verifyInstagram").click(function(){
      var buttonid = $(this).attr('id');
      var usernameid = "#instagramUsername" + buttonid;
      var instagramUsername = $(usernameid).val();
      if (!instagramUsername.trim() || instagramUsername.length == 0){
        alert("Enter an Instagram username to verify.");
      } else if (hasWhiteSpace(instagramUsername.trim())){
        alert("Instagram username should not contain spaces.")
      } else if (hasatsymbol(instagramUsername.trim())){
        alert("Do not include '@' in Instagram username.")
      } else{
        instagramLink = "https://www.instagram.com/" + instagramUsername.trim();
        window.open(instagramLink, '_blank')
      }
   });
});

$(function() {
   $(".saveBlacklistButton").click(function(){
      if (confirm("Once saved, it can\'t be modified for the next 15 days.\n\nAre you sure you want to save it?")){
         $(this).submit();
      } else{
      event.preventDefault();
      }
   });
});