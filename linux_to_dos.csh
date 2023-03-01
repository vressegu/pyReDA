
set All_pythonFile = ` find python_scripts_linux -name "*.py" | sed s/"python_scripts_linux\/"//g `

\cp -R python_scripts_linux python_scripts_win

# foreach pythonFile ( ${All_pythonFile} )
#   
#   echo ""
#   echo ""
#   echo "Unix to DOS python_scripts_linux/${pythonFile} -> Cf. python_scripts_win/${pythonFile}"
#   echo ""
#   unix2dos -n python_scripts_linux/${pythonFile} python_scripts_win/${pythonFile}
#   
# end

foreach pythonFile ( ${All_pythonFile} )
  
  echo ""
  echo ""
  echo "Unix to DOS python_scripts_linux/${pythonFile} -> Cf. python_scripts_win/${pythonFile}"
  echo ""
  unix2dos python_scripts_win/${pythonFile}
  
end
