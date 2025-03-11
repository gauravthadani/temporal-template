default: 
    just --list

export language := env("SDK_LANG", "go")
just_file := "$language.just"

print:
    @echo LANGUAGE is {{language}}, just_file is {{just_file}}

# clones a specific sample from the temporal samples, use this build upon what you want
[group("CLONE")]
copy SAMPLE:
    @echo Cloning github.com:temporalio/samples-{{language}}.git
    git clone --filter=blob:none --sparse org-56493103@github.com:temporalio/samples-{{language}}.git code 
    cd code && git sparse-checkout set {{SAMPLE}}

    echo "Finished Cloning, initialising"
    @just --justfile {{just_file}} init {{SAMPLE}}

create-new NAME:
    mkdir code
    @just --justfile {{just_file}} create-new {{NAME}}

[group("temporal")]
start-temporal:
    temporal server start-dev --db-filename local

print-workflows:
    temporal workflow list

[group("temporal")]
start-worker SAMPLE:
    @just --justfile {{just_file}} start-worker {{SAMPLE}}

[group("temporal")]
start-starter SAMPLE:
    @just --justfile {{just_file}} start-starter {{SAMPLE}}

[confirm]
clean:
    rm -rf code 