-- Resolve canonical Markdown engineering notes to their rendered guide pages.
local guides = {design=true, hardware=true, protocol=true, build=true,
  bringup=true, calibration=true, course=true, proposal=true,
  ['design-review']=true, midpoint=true, checkoff=true,
  verification=true, references=true}
function Link(el)
  if not el.target:match('^%a[%w+.-]*:') then
    local base = el.target:match('([^/]+)%.md[#?]?.*$')
    if base and guides[base] then
      el.target = el.target:gsub('%.md([#?]?)', '.html%1', 1)
    end
  end
  return el
end
