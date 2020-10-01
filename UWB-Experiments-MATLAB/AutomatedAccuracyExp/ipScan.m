function [tagIp, tagMAC] = ipScan(hostIp, subnetMask)
    % Scan the ip address of tags in the same WLAN network
    % Dependency: nmap available at https://nmap.org/download.html
    cleanup = onCleanup(@()myCleanup());
    tagIp = {};
    tagMAC = {};
    
    subnetSegment = extractNetSeg(hostIp, subnetMask);
    if(ispc)
        % Nmap is installed with administrator privilege
        [status, nmapOut] = system(char(strcat('nmap -sP',{' '},subnetSegment,...
            {' '},{'--exclude'},{' '},hostIp)));
    elseif(isunix || ismac)
        % MAC address won't show without sudo
        [status, nmapOut] = system(char(strcat('sudo nmap -sP',{' '},subnetSegment,...
            {' '},{'--exclude'},{' '},hostIp)));
    end
    nmapOutLines = splitlines(nmapOut);
    trimmedNmapOut = nmapOutLines(2:end-2);
    try
        for i = 3:1:length(trimmedNmapOut)
            detectedIdxCell = regexp(trimmedNmapOut(i), 'Raspberry Pi');
            if(isempty(detectedIdxCell{1}))
                continue
            else
                detectedIp = regexp(trimmedNmapOut(i-2),'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}','match');
                detectedMac = regexp(trimmedNmapOut(i),'([0-9A-F]{2}:){5}[0-9A-F]{2}','match');
                tagIp(length(tagIp)+1) = detectedIp;
                tagMAC(length(tagMAC)+1) = detectedMac;
            end
        end
    catch ME
        disp(nmapOutLines);
        disp(size(nmapOutLines));
        rethrow(ME);
    end
end

function netSegment = extractNetSeg(ip, subnetMask)
    % Extract the net IP segment as ***.***.***.***/**
    ipStr = split(ip, '.');
    maskStr = split(subnetMask, '.');
    ipDec = cellfun(@str2num, ipStr);
    maskDec = cellfun(@str2num, maskStr);
    ipSegmentDec = reshape(bitand(ipDec, maskDec),[size(ipDec,2),size(ipDec,1)]);
    ipSegmentStr = strjoin(arrayfun(@num2str, ipSegmentDec, 'UniformOutput',false),'.');
    slashLength = length(strfind(reshape(dec2bin(maskDec),[1,32]),'1'));
    netSegment = strcat(ipSegmentStr, {'/'},num2str(slashLength));
end

function myCleanup()
    fprintf('\n Close ALL \n');
    fclose("all");
    disp(pwd)
    clear;
end