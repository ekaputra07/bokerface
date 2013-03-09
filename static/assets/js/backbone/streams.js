// Post Model
var Post = Backbone.Model.extend({});

// Post collections
var Posts = Backbone.Collection.extend({

    model: Post,

    initialize: function([], options){
        this.query = options.query || '';
    },

    url: function(){
        return '/streams?'+this.query;
    },

    parse: function(resp){
        return resp.objects;
    }

});