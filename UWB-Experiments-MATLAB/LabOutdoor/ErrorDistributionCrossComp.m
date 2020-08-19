function CrossCompare()
    dinfo = dir('OUTDOOR*');
    filenames = {dinfo.name};
    XerrorABS = zeros(1,1);
    YerrorABS = zeros(1,1);
    figure(1);
    figure(2);
    for i=1:length(filenames)
        load(filenames(i)+"/Error","Xerror", "Yerror");
        XerrorABS = Xerror;
        %XerrorABS = abs(Xerror);
        x = linspace(min(XerrorABS),max(XerrorABS));
        xmean = mean(XerrorABS);
        xsd = std(XerrorABS);
        figure(1);
        hold on;
        cdfplot(XerrorABS);
        
        figure(2);
        hold on;
        plot(x,evcdf(x,xmean,xsd),"+-");
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