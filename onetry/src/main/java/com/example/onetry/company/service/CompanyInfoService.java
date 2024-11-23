package com.example.onetry.company.service;

import com.example.onetry.company.entity.CompanyExtraInfo;
import com.example.onetry.company.entity.CompanyInfo;
import com.example.onetry.company.repository.CompanyExtraInfoRepository;
import com.example.onetry.company.repository.CompanyInfoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class CompanyInfoService {

    private final CompanyInfoRepository companyInfoRepository;
    private final CompanyExtraInfoRepository companyExtraInfoRepository;

    // 전체 CompanyInfo 목록 조회
    public List<CompanyInfo> getAllCompanyInfo() {
        List<CompanyInfo> companyInfoList = companyInfoRepository.findAll();
        return companyInfoList;
    }

    // 특정 CompanyInfo 조회
    public CompanyInfo getCompanyInfoById(Long id) {
        CompanyInfo companyInfo = companyInfoRepository.findByInfoNo(id);
        return companyInfo;
    }

    public List<CompanyExtraInfo> getAllCompanyExtraInfo() {
        List<CompanyExtraInfo> companyExtraInfos = companyExtraInfoRepository.findAll();
        return companyExtraInfos;
    }
    public CompanyExtraInfo getCompanyExtraInfoById(Long id) {
        CompanyExtraInfo companyExtraInfo = companyExtraInfoRepository.findByInfoNo(id);
        return companyExtraInfo;
    }

    public List<String> getCompanyNames() {
        List<String> companyNames = companyInfoRepository.findAllCompanyNames();
        return companyNames;
    }
}
