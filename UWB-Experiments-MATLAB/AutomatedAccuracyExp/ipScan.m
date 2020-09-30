function [tagDeviceIpInfo] = ipScan(hostIp, subnetMask)
    %Scan the ip address of tags in the same WLAN network
    subnetSegment = extractNetSeg(hostIp, subnetMask);
    if(ispc)
        [status, nmapOut] = system(strcat({'nmap -sP'},{' '},{subnetSegment}));
    elseif(isunix)
        % MAC address won't show without sudo
        [status, nmapOut] = system(strcat({'sudo nmap -sP'},{' '},{subnetSegment}))
     
end

function netSegment = extractNetSeg(ip, subnetMask)
    %Extract the net IP segment as ***.***.***.0/24
end