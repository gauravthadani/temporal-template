default: 
    just --list

export LANGUAGE := "go"
just_file := "$LANGUAGE.just"

# clones a specific sample from the temporal $LANGUAGE samples, use this build upon what you want
copy SAMPLE:
    git clone --filter=blob:none --sparse org-56493103@github.com:temporalio/samples-$LANGUAGE.git code 
    cd code;  
    git sparse-checkout set {{SAMPLE}}

start-temporal:
    temporal server start-dev --db-filename local

print-workflows:
    temporal workflow list

start-worker SAMPLE:
    @just --justfile {{just_file}} start-worker {{SAMPLE}}

start-starter SAMPLE:
    @just --justfile {{just_file}} start-starter {{SAMPLE}}

[confirm]
clean:
    rm -rf code 