function CrossCompare()
    dinfo = dir('OUTDOOR*');
    filenames = {dinfo.name};
    XerrorABS = zeros(1,1);
    YerrorABS = zeros(1,1);
    figure();
    for i=1:length(filenames)
        load(filenames(i)+"/Error","Xerror", "Yerror");
        XerrorABS = abs(Xerror);
        x = linspace(min(XerrorABS),max(XerrorABS));
        xmean = mean(XerrorABS);
        xsd = std(XerrorABS); 
        %cdfplot(XerrorABS);
        %hold on;
        plot(x,evcdf(x,xmean,xsd),"b+-");
        %YerrorABS = abs(Yerror);
        hold on;
    end
    legend([filenames],"location","best")

end

function myCleanup()
    fprintf('\n Close ALL \n');
    fclose("all");
    clear;
    cd ..
end