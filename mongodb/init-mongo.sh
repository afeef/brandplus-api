#!/bin/sh

set -eu

mongosh -- "$MONGODB_DATABASE" <<EOF
    var rootUser = '$MONGO_INITDB_ROOT_USERNAME';
    var rootPassword = '$MONGO_INITDB_ROOT_PASSWORD';
    var admin = db.getSiblingDB('admin');
    admin.auth(rootUser, rootPassword);
    var mongoDatabase = '$MONGODB_DATABASE';
    db = db.getSiblingDB(mongoDatabase);
    var user = '$MONGODB_USER';
    var password = '$MONGODB_PASSWORD';
    db.createUser(
        {
            user: user,
            pwd: password,
            roles: [
                {
                    "role": "readWrite",
                    "db": mongoDatabase
                }
            ]
        }
    );
EOF
