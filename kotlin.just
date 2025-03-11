[working-directory: 'code']
create-new NAME:
    gradle init --type kotlin-application \
        --dsl kotlin \
        --project-name {{NAME}} \
        --package com.example.{{NAME}} \
        --test-framework kotlintest --java-version 21 --use-defaults

    idea ./
