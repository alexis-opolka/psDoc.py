
<#
    .DESCRIPTION
    This a test function used as an example of the output
    for psDoc.py

    .LINK
    The GitHub Homepage: https://github.com/alexis-opolka/psDoc.py

#>
function test {
    param (
        [parameter(Mandatory)]
        [string] $StringToEcho
    )

    Write-Output "$StringToEcho"
}

### We're calling the test function
test 'Hello World'
