/*
 * A collection of ajax function to support bokerface.com UI.
 * Author: Eka Putra @ekaputra07
 */

function app_push(action, params, callback){
    jQuery.post('/ajax-action?a='+action, params, function(resp){
        if(callback){
            callback(resp);
        }
    });
}