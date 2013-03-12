// Post Model
var Post = Backbone.Model.extend({});

// Post collections
var Posts = Backbone.Collection.extend({

    model: Post,

    initialize: function([], options){
        this.query = options.query || '';
        this.next_url = null;
    },

    url: function(){
        return '/streams?'+this.query;
    },

    parse: function(resp){
        this.next_url = resp.meta.next_url;
        return resp.objects;
    }

});