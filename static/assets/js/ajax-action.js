/*
 * A collection of ajax function to support bokerface.com UI.
 * Author: Eka Putra @ekaputra07
 */

function ajax_action(action, params, callback){
    jQuery.post('/ajax-action?a='+action, params, function(resp){
        if(callback){
            callback(resp);
        }
    });
}


jQuery(document).ready(function($){

     /* Like button in detail page */
     $('.btn-like-detail').click(function(){
        var boker = $(this).attr('data-boker'),
            that = this;
        ajax_action('like', {boker: boker}, function(){
            $(that).addClass('disabled');
        });
     });

     /* Like button in list page */
    $('body').on('click', '.btn-like-list', function(e){
        var boker = $(e.currentTarget).attr('data-boker'),
            that = e.currentTarget;
        ajax_action('like', {boker: boker}, function(){
            $(that).parent().parent().remove();
        });
    });
});
