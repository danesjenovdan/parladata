define({ "api": [  {    "type": "get",    "url": "/getMPs/:date",    "title": "Request information of all members",    "name": "GetMembers",    "group": "Members__",    "parameter": {      "fields": {        "Parameter": [          {            "group": "Parameter",            "type": "date",            "optional": false,            "field": "date",            "description": "<p>is optional parameter and *return members on this day. *</p>"          }        ]      }    },    "success": {      "fields": {        "Success 200": [          {            "group": "Success 200",            "type": "Json",            "optional": false,            "field": "return",            "description": "<p>arrayo f all members. Each elemnt is object of * member data.</p>"          },          {            "group": "Success 200",            "type": "String",            "optional": false,            "field": "lastname",            "description": "<p>Lastname of the User.</p>"          }        ]      }    },    "version": "0.0.0",    "filename": "./parladata/views.py",    "groupTitle": "Members__"  }] });
